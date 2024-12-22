from lib import CONN, CURSOR
from employee import Employee  # Imported within method to avoid circular imports

class Review:
    all = {}  # Class-level dictionary to cache instances
    
    def __init__(self, year, summary, employee, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee = employee

    def __repr__(self):
        return f"Review(id={self.id}, year={self.year}, summary={self.summary}, employee={self.employee})"

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews;")
        CONN.commit()

    # Save method
    def save(self):
        if self.id is None:
            CURSOR.execute("""
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?);
            """, (self.year, self.summary, self.employee.id))
            self.id = CURSOR.lastrowid  # Set the ID from the database
        else:
            CURSOR.execute("""
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?;
            """, (self.year, self.summary, self.employee.id, self.id))
        CONN.commit()
        Review.all[self.id] = self  # Cache the instance by its ID

    # Class method to create a new Review
    @classmethod
    def create(cls, year, summary, employee):
        review = cls(year, summary, employee)
        review.save()
        return review

    # Class method to get an instance from the database
    @classmethod
    def instance_from_db(cls, row):
        if row[0] in cls.all:
            return cls.all[row[0]]
        else:
            employee = Employee.find_by_id(row[3])  # Assuming employee exists
            review = cls(row[0], row[1], row[2], row[3])
            cls.all[row[0]] = review
            return review

    # Class method to find a review by id
    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute("SELECT * FROM reviews WHERE id = ?;", (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    # Method to update a review's details
    def update(self):
        self.save()  # Re-use the save method for updates

    # Method to delete a review
    def delete(self):
        CURSOR.execute("DELETE FROM reviews WHERE id = ?;", (self.id,))
        CONN.commit()
        del Review.all[self.id]  # Remove from cache
        self.id = None  # Set the id to None as it's deleted

    # Class method to get all reviews
    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM reviews;")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # Property for year validation
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if value < 2000:
            raise ValueError("Year must be >= 2000.")
        self._year = value

    # Property for summary validation
    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not value:
            raise ValueError("Summary must be a non-empty string.")
        self._summary = value

    # Property for employee validation
    @property
    def employee(self):
        return self._employee

    @employee.setter
    def employee(self, value):
        if not isinstance(value, Employee):
            raise ValueError("Employee must be an instance of Employee class.")
        self._employee = value
