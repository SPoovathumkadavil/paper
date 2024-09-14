import constants
import click
import db

@click.group()
@click.option("-t", "--test", is_flag=True, default=False, help="sets test directories for library and config")
def main(test):
    # test mode
    if test:
        constants.TEST = True
    constants.update()

@main.command()
def test():
    print(constants.DB_DIR)
    print("creating db ...")
    DB = db.PaperDB()
    DB.create_db()

if __name__ == "__main__":
    main()
