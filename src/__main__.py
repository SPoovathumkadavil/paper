import boilerutils
import click

@click.group()
@click.option("-t", "--test", is_flag=True, default=False, help="sets test directories for library and config")
def main(test):
    # test mode
    if test:
        boilerutils.TEST = True
    boilerutils.update()

if __name__ == "__main__":
    main()
