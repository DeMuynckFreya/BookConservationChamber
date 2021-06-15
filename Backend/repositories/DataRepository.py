from .Database import Database
import datetime

class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

### AUTHOR ###
    ## Create
    @staticmethod   
    def add_author(firstName,lastName,countryCode='UN'): 
        sql = "INSERT INTO Author (FirstName, LastName, CountryCode) VALUES (%s, %s, %s)"
        params = [firstName, lastName, countryCode]
        return Database.execute_sql(sql, params)

    ## Read
    @staticmethod
    def read_all_authors():
        sql = "SELECT * FROM Author WHERE AuthorID > 0"
        return Database.get_rows(sql)

    @staticmethod
    def read__authors_by_country(countryCode):
        sql = "SELECT * FROM Author WHERE CountryCode = %s"
        params = [countryCode]
        return Database.get_one_row(sql, params)

    @staticmethod
    def read__author_by_id(authorId):
        sql = "SELECT * FROM Author WHERE AuthorID = %s"
        params = [authorId]
        return Database.get_one_row(sql, params)
    
    @staticmethod
    def read__author_by_name(firstName, lastName):
        sql = "SELECT AuthorID FROM Author where FirstName = %s and LastName = %s;"
        params = [firstName,lastName]
        return Database.get_rows(sql, params)

    ## Update
    @staticmethod
    def update_author(authorId, firstName, lastName, countryCode):
        sql = "UPDATE Author SET FirstName = %s, LastName = %s, CountryCode = %s WHERE (AuthorID = %s)"
        params = [firstName, lastName, countryCode, authorId]
        return Database.execute_sql(sql, params)

    ## Delete
    @staticmethod
    def delete_author(authorId):
        sql = "DELETE FROM Author WHERE (AuthorID = %s)"
        params = [authorId]
        return Database.execute_sql(sql, params)

### COUNTRY ###
    ## Create
    @staticmethod
    def create_country(country_code, country):
        sql = "INSERT INTO Country (CountryCode, Country) VALUES (%s, %s)"
        params = [country_code, country]
        return Database.execute_sql(sql, params)

    ## Read
    @staticmethod
    def read_countries():
        sql = "SELECT * FROM Country WHERE CountryCode != 'UN'"
        return Database.get_rows(sql)

    @staticmethod
    def read_country(country_code):
        sql = "SELECT * FROM Country WHERE CountryCode = %s"
        params = [country_code]
        return Database.get_one_row(sql, params)

    ## Update
    @staticmethod
    def update_country(country_code, country):
        sql = "UPDATE Country SET Country = %s WHERE (CountryCode = %s)"
        params = [country, country_code]
        return Database.execute_sql(sql, params)

    ## Delete
    @staticmethod
    def delete_country(country_code):
        sql = "DELETE FROM Country WHERE (CountryCode = %)"
        params = [country_code]
        return Database.execute_sql(sql, params)

### LANGUAGE ###
    ## Create
    @staticmethod
    def create_language(language_code, language):
        sql = "INSERT INTO Language (LanguageCode, Language) VALUES (%s, %s)"
        params = [language_code, language]
        return Database.execute_sql(sql, params)

    ## Read
    @staticmethod
    def read_languages():
        sql = "SELECT * FROM Language WHERE LanguageCode != 'un'"
        return Database.get_rows(sql)

    def read_language(language_code):
        sql = "SELECT * FROM Language WHERE LanguageCode = %s"
        params = [language_code]
        return Database.get_one_row(sql, params)

    ## Update
    @staticmethod
    def update_language(language_code, language):
        sql = "UPDATE Language SET Language = %s WHERE (LanguageCode = %s);"
        params = [language, language_code]
        return Database.execute_sql(sql, params)

    ## Delete
    @staticmethod
    def delete_language(language_code):
        sql = "DELETE FROM Language WHERE (LanguageCode = %s)"
        params = [language_code]
        return Database.execute_sql(sql, params)
    
### BOOK ###
    ## Create
    @staticmethod
    def create_book(rfid_uid, barcode, title, author_id, language_code, pages, present_in_chamber=0, img_path="img/defaultimg.jpg"): 
        sql = "INSERT INTO Book (RfidUid, Barcode, Title, AuthorID, LanguageCode, Pages, ImgPath, PresentInChamber) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        params = [rfid_uid, barcode, title, author_id, language_code, pages, img_path, present_in_chamber]
        return Database.execute_sql(sql, params)

    ## Read
    @staticmethod
    def read_books():
        sql = "SELECT * FROM Book WHERE BookID > 0"
        return Database.get_rows(sql)
    
    @staticmethod
    def read_books_and_author():
        sql = "SELECT Book.*, Author.FirstName, Author.LastName, Author.CountryCode FROM Book JOIN Author ON Book.AuthorID = Author.AuthorID WHERE Book.BookID > 0"
        return Database.get_rows(sql)

    @staticmethod
    def read_book(book_id):
        sql = "SELECT * FROM Book WHERE BookID = %s"
        params = [book_id]
        return Database.get_one_row(sql, params)

    @staticmethod
    def read_book_by_rfid(rfid_uid):
        sql = "SELECT * FROM Book WHERE RfidUid = %s"
        params = [rfid_uid]
        return Database.get_one_row(sql, params)

    @staticmethod
    def read_books_by_author(author_id):
        sql = "SELECT Book.*, Author.FirstName, Author.LastName, Author.CountryCode FROM Book JOIN Author ON Book.AuthorID = Author.AuthorID WHERE Book.AuthorID = %s"
        params = [author_id]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_books_by_language(language_code):
        sql = "SELECT * FROM Book WHERE LanguageCode = %s"
        params = [language_code]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_books_by_present_in_chamber(present_in_chamber):
        sql = "SELECT Book.*, Author.FirstName, Author.LastName, Author.CountryCode FROM Book JOIN Author ON Book.AuthorID = Author.AuthorID WHERE Book.PresentInChamber = %s"
        params = [present_in_chamber]
        return Database.get_rows(sql, params)

    ## Update
    @staticmethod
    def update_book_present_in_chamber(status, id):
        sql = "UPDATE Book SET PresentInChamber = %s WHERE (BookID = %s)"
        params = [status, id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def update_book(book_id, rfid_uid, barcode, title, author_id, language_code, pages, img_path, present_in_chamber):
        sql = "UPDATE Book SET RfidUid = %s, Barcode = %s, Title = %s, AuthorID = %s, LanguageCode = %, Pages = %s, ImgPath = %s, PresentInChamber = %s WHERE (`BookID` = %s)"
        params = [rfid_uid, barcode, title, author_id, language_code, pages, img_path, present_in_chamber, book_id]
        return Database.execute_sql(sql, params)

    ## Delete
    @staticmethod
    def delete_book(book_id):
        sql = "DELETE FROM Book WHERE (BookID = %s)"
        params= [book_id]
        return Database.execute_sql(sql, params)

### COMPONENT ###
    ## Create
    @staticmethod
    def create_component(name, unit, description="No description given"):
        sql = "INSERT INTO Component (Name, Unit, Description) VALUES (%s, %s, %s)"
        params = [name, unit, description]
        return Database.execute_sql(sql, params)

    ## Read
    @staticmethod
    def read_components():
        sql = "SELECT * FROM Component WHERE ComponentID > 0"
        return Database.get_rows(sql)
    
    @staticmethod
    def read_component(component_id):
        sql = "SELECT * FROM Component WHERE ComponentID = %s"
        params = [component_id]
        return Database.get_one_row(sql, params)

    ## Update 
    @staticmethod
    def update_component(component_id, name, unit, description):
        sql = "UPDATE Component SET Name = %s, Unit = %s, Description = %s WHERE (ComponentID = %s)"
        params = [name, unit, description, component_id]
        return Database.execute_sql(sql, params)

    ## Delete 
    def delete_component(component_id):
        sql = "DELETE FROM Component WHERE (ComponentID = %s);"
        params = [component_id]
        return Database.execute_sql(sql, params)

### HISTORY ###
    ## Create 
    @staticmethod
    def create_history(entry_date, value, action, rfid_uid, component_id, book_id):
        sql = "INSERT INTO History (EntryDate, Value, Action, RfidUid, ComponentID, BookID) VALUES (%s, %s, %s, %s, %s, %s)"
        params = [entry_date, value, action, rfid_uid, component_id, book_id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def create_sensor_history(component_id, value):
        sql = "INSERT INTO History (Value, ComponentID) VALUES (%s, %s)"
        params = [value, component_id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def create_actuator_history(component_id, action):
        sql = "INSERT INTO History (Action, ComponentID) VALUES (%s, %s)"
        params = [action, component_id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def create_rfid_history(component_id, rfid_id, book_id):
        sql = "INSERT INTO History (RfidUid, ComponentID, BookID) VALUES (%s, %s, %s)"
        params = [rfid_id, component_id, book_id]
    
    ## Read
    @staticmethod
    def read_history(limit=4294967295):
        sql = "SELECT * FROM History ORDER BY EntryDate DESC LIMIT %s"
        params = limit
        return Database.get_rows(sql, params)

    @staticmethod
    def read_component_history(component_id, limit=4294967295):
        sql = "SELECT * FROM History WHERE ComponentID = %s ORDER BY EntryDate DESC LIMIT %s "
        params = [component_id, limit]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_component_history_by_day(component_id, day, month, year):
        sql = "SELECT * FROM History WHERE ComponentID = %s AND DAY(EntryDate) = %s AND MONTH(EntryDate) = %s AND YEAR(EntryDate) = %s"
        params = (component_id, day, month, year)
        return Database.get_rows(sql, params)
        
    ## Update
    @staticmethod
    def update_history(entry_id, entry_date, value, action, rfid_uid, component_id, book_id):
        sql = "UPDATE History SET EntryDate = %s, Value = %s, Action = %s, RfidUid = %s, ComponentID = %s, BookID = %s WHERE (EntryID = %s)"
        params = [entry_date, value, action, rfid_uid, component_id, book_id, entry_id]
        return Database.execute_sql(sql, params)

    ## Delete
    @staticmethod
    def delete_history(entry_id):
        sql = "DELETE FROM History WHERE (EntryID = %s)"
        params = [entry_id]
        return Database.execute_sql(sql, params)