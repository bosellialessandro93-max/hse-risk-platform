"""External MySQL/PostgreSQL storage for accounts/options. Domain records use the same DB through PHP."""
import base64
import hashlib
import hmac
import re
import secrets
import ssl
from urllib.parse import urlsplit, unquote, parse_qs
from contextlib import contextmanager

import pymysql


def validated_config(config):
    config = dict(config)
    if config.get('url'):
        try:
            parts = urlsplit(config['url'])
            if parts.scheme not in ('postgresql', 'postgres') or not parts.hostname:
                raise ValueError()
            options = parse_qs(parts.query)
            config.update(driver='postgresql', host=parts.hostname, port=parts.port or 5432,
                          user=unquote(parts.username or ''), password=unquote(parts.password or ''),
                          name=unquote(parts.path.lstrip('/')),
                          sslmode=options.get('sslmode', ['verify-full'])[0],
                          channel_binding=options.get('channel_binding', ['prefer'])[0])
        except (ValueError, TypeError):
            raise ValueError('URL PostgreSQL non valido.') from None
    config.setdefault('driver', 'mysql')
    if config['driver'] not in ('mysql', 'postgresql'):
        raise ValueError('Database supportati: mysql e postgresql.')
    if config['driver'] == 'postgresql':
        config.setdefault('sslmode', 'verify-full')
        config.setdefault('sslrootcert', ssl.get_default_verify_paths().cafile)
        if config['sslmode'] not in ('verify-full', 'require', 'disable'):
            raise ValueError('sslmode PostgreSQL: verify-full o require (disable solo per test locali).')
        if config.get('channel_binding', 'prefer') not in ('prefer', 'require', 'disable'):
            raise ValueError('channel_binding PostgreSQL non valido.')
    required = ('host', 'user', 'password', 'name')
    if any(key not in config or (not config[key] and key != 'password') for key in required):
        raise ValueError('Configurare host, user, password e name del database esterno.')
    result = dict(config)
    result.setdefault('prefix', 'st_')
    result.setdefault('tls', True)
    if not re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_]{0,30}', result['prefix']):
        raise ValueError('Prefisso database non valido.')
    return result


@contextmanager
def connection(config):
    config = validated_config(config)
    if config['driver'] == 'postgresql':
        import psycopg
        from psycopg.rows import dict_row
        db = psycopg.connect(host=config['host'], port=int(config.get('port', 5432)),
                             user=config['user'], password=config['password'], dbname=config['name'],
                             sslmode=config['sslmode'], sslrootcert=config.get('sslrootcert'),
                             channel_binding=config.get('channel_binding', 'prefer'),
                             connect_timeout=10, row_factory=dict_row)
        try:
            with db.cursor() as cur:
                cur.execute("SET LOCAL TIME ZONE 'UTC'")
                cur.execute("SET LOCAL statement_timeout = '30s'")
                cur.execute("SET LOCAL lock_timeout = '10s'")
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
        return
    context = None
    if config['tls']:
        context = ssl.create_default_context()
        if config.get('ca_certificate'):
            context.load_verify_locations(cadata=config['ca_certificate'])
    db = pymysql.connect(host=config['host'], port=int(config.get('port', 3306)),
                         user=config['user'], password=config['password'], database=config['name'],
                         charset='utf8mb4', ssl=context, connect_timeout=10,
                         read_timeout=30, write_timeout=30, autocommit=False,
                         cursorclass=pymysql.cursors.DictCursor)
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def password_hash(password):
    if not isinstance(password, str) or len(password) < 12 or len(password) > 512:
        raise ValueError('Password: da 12 a 512 caratteri.')
    salt = secrets.token_bytes(16)
    value = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 600_000)
    return 'pbkdf2_sha256$600000$' + base64.b64encode(salt).decode() + '$' + base64.b64encode(value).decode()


def password_matches(password, encoded):
    try:
        algorithm, rounds, salt, value = encoded.split('$')
        if algorithm != 'pbkdf2_sha256' or not 100_000 <= int(rounds) <= 2_000_000:
            return False
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), base64.b64decode(salt), int(rounds))
        return hmac.compare_digest(actual, base64.b64decode(value))
    except (ValueError, TypeError, AttributeError):
        return False


def initialize(config, auth):
    config = validated_config(config)
    if config['driver'] == 'postgresql':
        return initialize_postgres(config, auth)
    prefix = config['prefix']
    with connection(config) as db, db.cursor() as cur:
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {prefix}users (
            id BIGINT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(254) NOT NULL UNIQUE,
            email VARCHAR(254) NULL UNIQUE, display_name VARCHAR(120) NOT NULL,
            password_hash VARCHAR(512) NOT NULL DEFAULT '', is_admin BOOLEAN NOT NULL DEFAULT 0,
            active BOOLEAN NOT NULL DEFAULT 1, token_version BIGINT NOT NULL DEFAULT 1, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')
        cur.execute(f"SHOW COLUMNS FROM {prefix}users LIKE 'token_version'")
        if not cur.fetchone():
            cur.execute(f'ALTER TABLE {prefix}users ADD COLUMN token_version BIGINT NOT NULL DEFAULT 1')
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {prefix}options (
            name VARCHAR(190) PRIMARY KEY, value LONGTEXT NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {prefix}login_limits (
            username VARCHAR(254) PRIMARY KEY, failures INT NOT NULL DEFAULT 0,
            last_failure DATETIME NULL, locked_until DATETIME NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')
        # An advisory lock serializes the one-time administrator bootstrap across workers.
        cur.execute('SELECT GET_LOCK(%s, 10) AS acquired', (prefix + 'hse_bootstrap',))
        if cur.fetchone()['acquired'] != 1:
            raise RuntimeError('Inizializzazione occupata; riprovare.')
        try:
            cur.execute(f'SELECT COUNT(*) AS n FROM {prefix}users')
            if cur.fetchone()['n'] == 0 and auth.get('mode', 'password') == 'password':
                username, password = auth.get('bootstrap_username'), auth.get('bootstrap_password')
                if username and password:
                    if password.startswith('REPLACE_'):
                        raise ValueError('Sostituire la password bootstrap di esempio.')
                    cur.execute(f'INSERT INTO {prefix}users (username,display_name,password_hash,is_admin) VALUES (%s,%s,%s,1)',
                                (username.casefold().strip(), 'Amministratore', password_hash(password)))
                    db.commit()
        finally:
            cur.execute('SELECT RELEASE_LOCK(%s)', (prefix + 'hse_bootstrap',))


def public_user(row):
    return {key: row[key] for key in ['id', 'username', 'display_name', 'is_admin', 'active', 'token_version']}


def get_user(config, user_id):
    with connection(config) as db, db.cursor() as cur:
        cur.execute(f'SELECT * FROM {config["prefix"]}users WHERE id=%s AND active=1', (user_id,))
        row = cur.fetchone()
        return public_user(row) if row else None


def authenticate(config, username, password):
    username = username.casefold().strip()[:254]
    prefix = config['prefix']
    with connection(config) as db, db.cursor() as cur:
        pg = validated_config(config)['driver'] == 'postgresql'
        sql = f'INSERT INTO {prefix}login_limits (username) VALUES (%s) ON CONFLICT DO NOTHING' if pg else f'INSERT IGNORE INTO {prefix}login_limits (username) VALUES (%s)'
        cur.execute(sql, (username,))
        now = 'CURRENT_TIMESTAMP' if pg else 'UTC_TIMESTAMP()'
        cur.execute(f'SELECT *, locked_until > {now} AS locked FROM {prefix}login_limits WHERE username=%s FOR UPDATE', (username,))
        limits = cur.fetchone()
        if limits['locked']:
            return None
        cur.execute(f'SELECT * FROM {prefix}users WHERE username=%s AND active=1', (username,))
        user = cur.fetchone()
        # Equal-cost verification also for missing/disabled identities.
        dummy = 'pbkdf2_sha256$600000$AAAAAAAAAAAAAAAAAAAAAA==$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='
        ok = password_matches(password[:512], user['password_hash'] if user else dummy)
        if ok and user:
            cur.execute(f'DELETE FROM {prefix}login_limits WHERE username=%s', (username,))
            return public_user(user)
        if pg:
            cur.execute(f'''UPDATE {prefix}login_limits SET
                failures=CASE WHEN last_failure < CURRENT_TIMESTAMP-INTERVAL '15 minutes' THEN 1 ELSE failures+1 END,
                locked_until=CASE WHEN (CASE WHEN last_failure < CURRENT_TIMESTAMP-INTERVAL '15 minutes' THEN 1 ELSE failures+1 END)>=5 THEN CURRENT_TIMESTAMP+INTERVAL '15 minutes' ELSE NULL END,
                last_failure=CURRENT_TIMESTAMP WHERE username=%s''', (username,))
            return None
        cur.execute(f'''UPDATE {prefix}login_limits SET failures=IF(last_failure < UTC_TIMESTAMP()-INTERVAL 15 MINUTE,1,failures+1),
            locked_until=IF(failures>=5,UTC_TIMESTAMP()+INTERVAL 15 MINUTE,NULL),last_failure=UTC_TIMESTAMP() WHERE username=%s''', (username,))
        return None


def oidc_user(config, identity, auth):
    if identity.get('email_verified') is not True:
        raise ValueError('Il provider deve fornire un indirizzo email verificato.')
    email = str(identity.get('email', '')).strip().casefold()
    if '@' not in email or len(email) > 254:
        raise ValueError('Email OIDC non valida.')
    domains = auth.get('allowed_domains', [])
    if domains and email.split('@')[-1] not in domains:
        raise ValueError('Dominio email non autorizzato.')
    admin = email in [v.casefold() for v in auth.get('admin_emails', [])]
    with connection(config) as db, db.cursor() as cur:
        cur.execute(f'SELECT * FROM {config["prefix"]}users WHERE email=%s FOR UPDATE', (email,))
        user = cur.fetchone()
        if not user:
            pg = validated_config(config)['driver'] == 'postgresql'
            cur.execute(f'INSERT INTO {config["prefix"]}users (username,email,display_name,is_admin) VALUES (%s,%s,%s,%s)' + (' RETURNING id' if pg else ''),
                        (email, email, str(identity.get('name', email))[:120], int(admin)))
            uid = cur.fetchone()['id'] if pg else cur.lastrowid
            cur.execute(f'SELECT * FROM {config["prefix"]}users WHERE id=%s', (uid,))
            user = cur.fetchone()
        if not user['active']:
            raise ValueError('Account disabilitato.')
        return public_user(user)


def manage_users(config, actor, *, create=None, update=None):
    current = get_user(config, actor['id'])
    if not current or not current['is_admin']:
        raise PermissionError('Solo amministratore.')
    prefix = config['prefix']
    with connection(config) as db, db.cursor() as cur:
        if create:
            username = create['username'].strip().casefold()
            if not username or len(username) > 254:
                raise ValueError('Nome utente non valido.')
            cur.execute(f'INSERT INTO {prefix}users (username,display_name,password_hash,is_admin) VALUES (%s,%s,%s,%s)',
                        (username, create['display_name'][:120] or username, password_hash(create['password']), int(bool(create.get('is_admin')))))
        if update:
            if int(update['id']) == int(actor['id']):
                raise ValueError('Gestire il proprio account da un altro amministratore.')
            if 'password' in update:
                cur.execute(f'UPDATE {prefix}users SET password_hash=%s,token_version=token_version+1 WHERE id=%s', (password_hash(update['password']), update['id']))
            else:
                cur.execute(f'UPDATE {prefix}users SET active=%s,is_admin=%s WHERE id=%s', (int(bool(update['active'])), int(bool(update['is_admin'])), update['id']))
        cur.execute(f'SELECT id,username,email,display_name,is_admin,active FROM {prefix}users ORDER BY id')
        return cur.fetchall()


def change_password(config, actor, old_password, new_password):
    with connection(config) as db, db.cursor() as cur:
        cur.execute(f'SELECT * FROM {config["prefix"]}users WHERE id=%s AND active=1 FOR UPDATE', (actor['id'],))
        row = cur.fetchone()
        if not row or not password_matches(old_password, row['password_hash']):
            raise ValueError('Password attuale non corretta.')
        cur.execute(f'UPDATE {config["prefix"]}users SET password_hash=%s,token_version=token_version+1 WHERE id=%s', (password_hash(new_password), actor['id']))
        return row['token_version'] + 1


def initialize_postgres(config, auth):
    prefix = config['prefix']
    with connection(config) as db, db.cursor() as cur:
        # Transaction-scoped lock works with Neon transaction pooling; no session lock leaks.
        cur.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))", (prefix + 'hse_bootstrap',))
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {prefix}users (
            id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY, username VARCHAR(254) NOT NULL UNIQUE,
            email VARCHAR(254) NULL UNIQUE, display_name VARCHAR(120) NOT NULL,
            password_hash VARCHAR(512) NOT NULL DEFAULT '', is_admin SMALLINT NOT NULL DEFAULT 0,
            active SMALLINT NOT NULL DEFAULT 1, token_version BIGINT NOT NULL DEFAULT 1,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        cur.execute(f'ALTER TABLE {prefix}users ADD COLUMN IF NOT EXISTS token_version BIGINT NOT NULL DEFAULT 1')
        cur.execute(f'CREATE TABLE IF NOT EXISTS {prefix}options (name VARCHAR(190) PRIMARY KEY, value TEXT NOT NULL)')
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {prefix}login_limits (
            username VARCHAR(254) PRIMARY KEY, failures INT NOT NULL DEFAULT 0,
            last_failure TIMESTAMP NULL, locked_until TIMESTAMP NULL)''')
        cur.execute(f'SELECT COUNT(*) AS n FROM {prefix}users')
        if cur.fetchone()['n'] == 0 and auth.get('mode', 'password') == 'password':
            username, password = auth.get('bootstrap_username'), auth.get('bootstrap_password')
            if username and password:
                if password.startswith('REPLACE_'):
                    raise ValueError('Sostituire la password bootstrap di esempio.')
                cur.execute(f'INSERT INTO {prefix}users (username,display_name,password_hash,is_admin) VALUES (%s,%s,%s,1)',
                            (username.casefold().strip(), 'Amministratore', password_hash(password)))
