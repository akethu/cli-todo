import click
from pyfiglet import Figlet
import sqlite3
from datetime import datetime

# Establishing connection with the local server
conn = sqlite3.connect('data.db')
c = conn.cursor()

def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS usersdata(username TEXT, password TEXT)')

def register_me(username, password):
    c.execute('CREATE TABLE IF NOT EXISTS todos(userpass TEXT, datetime TEXT, title TEXT, message TEXT)')
    c.execute('INSERT INTO usersdata(username, password) VALUES(?, ?)', (username, password))
    conn.commit()

def add_message(userpass, datetime, title, message):
    c.execute('INSERT INTO todos(userpass, datetime, title, message) VALUES(?, ?, ?, ?)', (userpass, datetime, title, message))
    conn.commit()

def delete_message(userpass, title):
    c.execute('DELETE FROM todos WHERE userpass="{}" AND title LIKE "%{}%"'.format(userpass, title))
    conn.commit()

def fetch_messages(userpass):
    c.execute('SELECT datetime, title, message FROM todos WHERE userpass="{}"'.format(userpass))
    data = c.fetchall()
    return data

def view_all_users():
    c.execute('SELECT username FROM usersdata')
    data = c.fetchall()
    return data 

def get_single_message(userpass, title):
    c.execute('SELECT datetime, title, message FROM todos WHERE userpass="{}" AND title="{}"'.format(userpass, title))
    data = c.fetchall()
    return data

def edit_single_user(username, password, newname):
    c.execute('UPDATE usersdata SET username="{}" WHERE username="{}" AND password="{}"'.format(newname, username, password))
    conn.commit()
    data = c.fetchall()
    return data

def search_message(userpass, title):
    c.execute('SELECT datetime, title, message FROM todos WHERE userpass="{}" AND title LIKE "{}"'.format(userpass, title))
    data = c.fetchall()
    return data

def check_user(username, password):
    c.execute('SELECT * FROM usersdata WHERE username="{}" AND password="{}"'.format(username, password))
    data = c.fetchall()
    return data

# To-do big font styling
f = Figlet(font='slant')
click.echo(f.renderText('Simple To-Do'))

# main function
@click.group()
@click.version_option(version='0.1', prog_name='To-Do Cloud')
def main():
    """ A simple To-do application (c) AdithyaKethu"""
    pass

# Command to register the user
@main.command()
@click.option('--username', '-un', prompt=True)
@click.password_option('--password', '-pw', prompt=True)
def register(username, password):
    """ Register before entering your To-do's """
    create_table()
    register_me(username, password)
    click.secho('Registered successfully.', fg='yellow')

# Command to add a to-do
@main.command()
@click.option('--username', '-un', prompt=True)
@click.password_option('--password', '-pw', prompt=True)
@click.option('--title', '-ti', prompt=True)
@click.option('--description', '-dc', prompt=True)
def add_todo(username, password, title, description):
    """ To add a todo task -- requires title and description of the task """
    userpass = username + password
    dt = datetime.now().strftime("%m/%d/%Y %H:%M:%S") 
    add_message(userpass, dt, title, description)
    result = check_user(username, password)
    if(len(result) == 0):
        click.secho('Username or password is wrong.', fg='red')
        click.secho("Type 'main.py register' if not registered yet.", fg='yellow')
    else:
        click.secho('To-Do task added', fg='yellow')
        click.secho("Type 'main.py view-todos' to view all To-do's", fg='blue')

# Command to delete a to-do
@main.command()
@click.option('--username', '-un', prompt=True)
@click.password_option('--password', '-pw', prompt=True)
@click.option('--title', '-ti', prompt=True)
def delete_todo(username, password, title):
    """ To delete a todo task -- requires title """
    userpass = username + password
    checking = check_user(username, password)
    if(len(checking) == 0):
        click.secho('Username or password is wrong.', fg='red')
        click.secho("Type 'main.py register' if not registered yet.", fg='yellow')
    
    else:
        click.secho('Deleting::{}'.format(title), fg='yellow')
        result = search_message(userpass, title)
        if(len(result) == 0):
            click.secho('No data found.', fg='red')
        else:
            delete_message(userpass, title)
            click.secho('To-Do task deleted.', fg='red')
            click.secho("Type 'main.py view-todos' to view all To-do's", fg='blue')

# Command to show all the users
@main.command()
def show_users():
    """ Show all users data in a table """
    from terminaltables import AsciiTable
    result = view_all_users()
    new_header = ['Username']
    click.secho('{}'.format(new_header), bg='blue')
    table1 = AsciiTable(result)
    click.echo(table1.table)

@main.command()
@click.option('--username', '-un', prompt=True)
@click.password_option('--password', '-pw', prompt=True)
def download_todos(username, password):
    """ Download all your To-do's into your current directory """
    from terminaltables import AsciiTable
    userpass = username + password
    result = fetch_messages(userpass)
    if(len(result) == 0):
        click.secho('Username or password is wrong.', fg='red')
        click.secho("Type 'main.py register' if not registered yet.", fg='yellow')
    else:
        table1 = AsciiTable(result)
        header = [['Data  &  Time    ', 'Title', ' Deescription    ']]
        table2 = AsciiTable(header)
        file = open("todo.txt", "w") 
        file.write(table2.table + '\n')
        file.write(table1.table) 
        file.close()
        click.secho('File has been downloaded. Check your current working directory.', fg='yellow')

# Command to search the title
@main.command()
@click.option('--username', '-un', prompt=True)
@click.password_option('--password', '-pw', prompt=True)
@click.option('--title', '-ti', prompt=True)
def search_title(username, password, title):
    """ Search for To-do's by their title """
    from terminaltables import AsciiTable
    userpass = username + password
    checking = check_user(username, password)
    if(len(checking) == 0):
        click.secho('Username or password is wrong.', fg='red')
        click.secho("Type 'main.py register' if not registered yet.", fg='yellow')
    else:
        click.secho('Searching for::{}'.format(title), fg='yellow')
        result = get_single_message(userpass, title)
        if(len(result) == 0):
            click.secho('No data found.', fg='red')
        else:
            table1 = AsciiTable(result)
            click.echo(table1.table)

# Command to edit the username
@main.command()
@click.option('--username', '-un', prompt=True)
@click.password_option('--password', '-pw', prompt=True)
@click.option('--newname', '-nn', prompt=True)
def edit_username(username, password, newname):
    """ Edit your username """
    from terminaltables import AsciiTable
    edit_single_user(username, password, newname)
    result = check_user(username, password)
    if(len(result) == 0):
        click.secho('Username or password is wrong.', fg='red')
        click.secho("Type 'main.py register' if not registered yet.", fg='yellow')
    else:
        click.secho('Editing:: {} and updating to {}'.format(username, newname))
        result1 = get_single_user(newname)
        table1 = AsciiTable(result)
        click.echo(table1.table)
        click.secho('Showing edited data', fg='yellow')

# Command to view all to-do's
@main.command()
@click.option('--username', '-un', prompt=True)
@click.password_option('--password', '-pw', prompt=True)
def view_todos(username, password):
    """ View all your To-do's """
    from terminaltables import AsciiTable
    userpass = username + password
    result = fetch_messages(userpass)
    if(len(result) == 0):
        click.secho('Username or password is wrong.', fg='red')
        click.secho("Type 'main.py register' if not registered yet.", fg='yellow')
    else:
        table1 = AsciiTable(result)
        header = [['Data  &  Time    ', 'Title', ' Deescription    ']]
        table2 = AsciiTable(header)
        click.echo(table2.table)
        click.echo(table1.table)

if __name__ == '__main__':
    main()

