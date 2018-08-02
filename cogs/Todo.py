import discord
from discord.ext import commands
import psycopg2
import os

DATABASE_URL = os.environ['DATABASE_URL']


class Todo:
    '''
    Commands for the to-do list.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def todo(self, ctx):
        '''
        To-do list commands.
        w.todo <subcommand>
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send("Subcommands: list, add, remove, check, clean")

    @todo.command()
    async def list(self, ctx):
        '''
        Your to-do list
        w.todo list
        '''
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT todo_list FROM users
                    WHERE ID = %s; """, (str(ctx.author.id), ))
        todo_list = c.fetchone()[0]
        if todo_list is None:
            await ctx.send("Your to-do list is empty! You can add a task with \"w.todo add <task>\".")
        else:
            description = ""
            for i in range(len(todo_list)):
                description += "**" + str(i+1) + ")** " + todo_list[i] + "\n"
            embed = discord.Embed(title=str(ctx.author.name) + "'s to-do list", description=description, color=0x48d1cc)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        conn.commit()
        conn.close()

    @todo.command()
    async def add(self, ctx, *, task):
        '''
        Adds a task to your to-do list.
        w.todo add <task>
        '''
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT todo_list FROM users
                    WHERE ID = %s; """, (str(ctx.author.id), ))
        todo_list = c.fetchone()[0]
        if todo_list is not None:
            if task in todo_list:
                await ctx.send("\"" + str(task) + "\" is already in your to-do list!")
                return
        c.execute(""" UPDATE users
                    SET todo_list = array_append(todo_list, %s) 
                    WHERE ID = %s; """, (str(task), str(ctx.author.id)))
        await ctx.send("Added task: \"" + str(task) + "\"")
        conn.commit()
        conn.close()

    @todo.command()
    async def remove(self, ctx, task_number):
        '''
        Removes a task from your to-do list.
        w.todo remove <task number>
        '''
        try:
            num = int(task_number)
        except:
            await ctx.send("You must input an integer.")
            return
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT todo_list FROM users
                    WHERE ID = %s; """, (str(ctx.author.id), ))
        todo_list = c.fetchone()[0]
        if todo_list is None:
            await ctx.send("Your to-do list is empty! You can add a task with \"w.todo add <task>\".")
        elif 1 <= num <= len(todo_list):
            task_to_remove = todo_list[num-1]
            c.execute(""" UPDATE users
                        SET todo_list = array_remove(todo_list, %s)
                        WHERE ID = %s; """, (task_to_remove, str(ctx.author.id)))
            await ctx.send("Removed task: \"" + task_to_remove + "\"")
        else:
            await ctx.send("You must input an integer between 1 and " + str(len(todo_list)))
        conn.commit()
        conn.close()

    @todo.command()
    async def check(self, ctx, task_number):
        '''
        Checks or unchecks a task from your to-do list.
        w.todo check <task number>
        '''
        try:
            num = int(task_number)
        except:
            await ctx.send("You must input an integer.")
            return
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT todo_list FROM users
                    WHERE ID = %s; """, (str(ctx.author.id), ))
        todo_list = c.fetchone()[0]
        if todo_list is None:
            await ctx.send("Your to-do list is empty! You can add a task with \"w.todo add <task>\".")
        elif 1 <= num <= len(todo_list):
            task_to_check = todo_list[num-1]
            if task_to_check[:2] == "~~" and task_to_check[-2:] == "~~":
                c.execute(""" UPDATE users
                            SET todo_list = array_replace(todo_list, %s, %s)
                            WHERE ID = %s; """, (task_to_check, task_to_check[2:-2], str(ctx.author.id)))
                await ctx.send("Unchecked task: \"" + task_to_check[2:-2] + "\"")
            else:
                c.execute(""" UPDATE users
                            SET todo_list = array_replace(todo_list, %s, %s)
                            WHERE ID = %s; """, (task_to_check, "~~"+task_to_check+"~~", str(ctx.author.id)))
                await ctx.send("Checked task: \"" + task_to_check + "\"")
        else:
            await ctx.send("You must input an integer between 1 and " + str(len(todo_list)))
        conn.commit()
        conn.close()

    @todo.command()
    async def clean(self, ctx):
        '''
        Completely cleans your to-do list.
        w.todo clean
        '''
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" UPDATE users
                    SET todo_list = Null
                    WHERE ID = %s; """, (str(ctx.author.id), ))
        await ctx.send("Your to-do list has been cleaned.")
        conn.commit()
        conn.close()


def setup(bot):
    bot.add_cog(Todo(bot))