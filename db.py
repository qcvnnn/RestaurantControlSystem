import sqlite3


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


con = sqlite3.connect("database.db")
con.row_factory = dict_factory
cur = con.cursor()


def getRestaurantStars(id):
    return cur.execute("SELECT SUM(stars)/COUNT(stars) AS stars FROM reviews WHERE restaurant_id = ?", (id,)) \
        .fetchone()['stars']


def getRestaurantInfo(id: int):
    result = cur.execute("SELECT * FROM restaurants WHERE id = ?", (id,)).fetchone()
    result['stars'] = getRestaurantStars(id)
    return result


def getReviewsInfo(restaurantId):
    return cur.execute("SELECT * FROM reviews WHERE restaurant_id = ?", (restaurantId,)).fetchall()


def getRestaurantInfoByName(name):
    result = cur.execute("SELECT * FROM restaurants WHERE name = ?", (name,)).fetchone()
    return result


def getReservationsInfo(user_id):
    return cur.execute("SELECT * FROM reservations WHERE user_id = ?", (user_id,)).fetchall()


def getAdminReservationsInfo():
    return cur.execute("SELECT * FROM reservations").fetchall()


def getAdminRestaurantInfo():
    return cur.execute("SELECT * FROM restaurants").fetchall()


def getTablesAmount(hour, date, id):
    num1 = cur.execute("SELECT * FROM reservations WHERE hour = ? AND date = ? AND restaurant_id = ?",
                       (hour, date, id,)).fetchall()
    num2 = cur.execute("SELECT tables_amount FROM restaurants WHERE id = ?", (id,)).fetchone()
    return str(num2['tables_amount'] - len(num1))


def getUserInfo(login: str):
    return cur.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchone()


def addUser(login, password):
    cur.execute("INSERT INTO users(login, password) VALUES(?,?)", (str(login), str(password)))
    return con.commit()


def addReview(login, text, stars, id):
    cur.execute("INSERT INTO reviews(user_login, text, stars, restaurant_id) VALUES(?,?,?,?)",
                (login, text, int(stars), id))
    return con.commit()


def addReservation(date, hour, restaurant_id, user_id):
    cur.execute("INSERT INTO reservations(date, hour, restaurant_id, user_id) VALUES(?,?,?,?)",
                (date, hour, restaurant_id, user_id,))
    return con.commit()


def addRestaurant(name, description, address, tables_amount, image):
    cur.execute("INSERT INTO restaurants(name, description, address, tables_amount, image) VALUES(?,?,?,?,?)",
                (name, description, address, tables_amount, image,))
    return con.commit()

def deleteReservation(id):
    cur.execute("DELETE FROM reservations WHERE id = ?", (id,))
    return con.commit()


def deleteRestaurant(id):
    cur.execute("DELETE FROM restaurants WHERE id = ?", (id,))
    return con.commit()


def searchRestaurant(query):
    result = cur.execute(
        f"SELECT id, name, address FROM restaurants WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
        f" OR address LIKE '%{query}%'").fetchall()
    for i in range(len(result)):
        if getRestaurantStars(result[i]['id']) == None:
            result[i]['stars'] = 0
        else:
            result[i]['stars'] = getRestaurantStars(result[i]['id'])

    return result


def searchInfo(query):
    result = cur.execute(
        f"SELECT id, user_id, restaurant_id, date, hour FROM reservations WHERE id LIKE '%{query}%' OR user_id LIKE "
        f"'%{query}%' OR restaurant_id LIKE '%{query}%' OR date LIKE '%{query}%' OR hour LIKE '%{query}%'").fetchall()

    return result
