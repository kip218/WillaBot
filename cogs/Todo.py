import discord
from discord.ext import commands
import psycopg2
import os
import asyncio

DATABASE_URL = os.environ['DATABASE_URL']


class Todo:
    '''
    Commands for the to-do list.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def todo(self, ctx):
        '''
        To-do list commands.
        w.todo <subcommand>

        Type "w.todo" for a list of subcommands.
        '''
        todo_group_command = self.bot.get_command('todo')
        subcommands_lst = []
        for subcommand in todo_group_command.commands:
            if subcommand.full_parent_name == 'todo':
                subcommands_lst.append(f"`{subcommand.name}`")
        help_msg = ', '.join(subcommands_lst)
        await ctx.send(f"**w.todo** subcommands: {help_msg}")

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
        conn.commit()
        conn.close()
        if todo_list is None:
            await ctx.send("Your to-do list is empty! You can add a task with \"w.todo add <task>\".")
        else:
            desc_lst = []
            description = ""
            for i in range(len(todo_list)):
                if len(description) > 1000:
                    desc_lst.append(description)
                    description = ""
                    description += f"**{i+1})** {todo_list[i]}\n"
                else:
                    description += f"**{i+1})** {todo_list[i]}\n"
            desc_lst.append(description)

        def get_embed(page_number):
            embed = discord.Embed(title=f"{ctx.author.name}'s to-do list", description=desc_lst[page_number-1], color=ctx.author.color)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_footer(text=f"Page {page_number} of {len(desc_lst)}")
            return embed

        def check(reaction, user):
                return ctx.message.author == user and user.bot is False and (reaction.emoji == '\U0001F448' or reaction.emoji == '\U0001F449') and todo_page.id == reaction.message.id

        embed_lst = []
        for i in range(len(desc_lst)):
            curr_embed = get_embed(i+1)
            embed_lst.append(curr_embed)

        curr_page = 1
        todo_page = await ctx.send(embed=embed_lst[curr_page-1])
        await todo_page.add_reaction(emoji='\U0001F448')
        await todo_page.add_reaction(emoji='\U0001F449')
        timeout = False
        while timeout is False:
            try:
                done, pending = await asyncio.wait([self.bot.wait_for('reaction_add', check=check, timeout=120), self.bot.wait_for('reaction_remove', check=check, timeout=120)], return_when=asyncio.FIRST_COMPLETED)
                reaction = done.pop().result()[0]
            except asyncio.TimeoutError:
                timeout = True
                todo_page_embed = todo_page.embeds[0]
                todo_page_embed.set_footer(text="The to-do list has timed out!")
                await todo_page.edit(embed=todo_page_embed)
                return
            else:
                if reaction.emoji == '\U0001F448':
                    if curr_page == 1:
                        curr_page = len(desc_lst)
                    else:
                        curr_page -= 1
                elif reaction.emoji == '\U0001F449':
                    if curr_page == len(desc_lst):
                        curr_page = 1
                    else:
                        curr_page += 1
                await todo_page.edit(embed=embed_lst[curr_page-1])

    @todo.command()
    async def add(self, ctx, *, task):
        '''
        Adds a task to your to-do list.
        w.todo add <task>
        '''
        if len(task) > 1000:
            await ctx.send("<task> must be less than 1000 characters!")
            return

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT todo_list FROM users
                    WHERE ID = %s; """, (str(ctx.author.id), ))
        todo_list = c.fetchone()[0]
        if todo_list is not None:
            if task in todo_list:
                await ctx.send("\"" + str(task) + "\" is already in your to-do list!")
                conn.close()  # Do I need this?
                return
        c.execute(""" UPDATE users
                    SET todo_list = array_append(todo_list, %s)
                    WHERE ID = %s; """, (str(task), str(ctx.author.id)))
        conn.commit()
        await ctx.send("Added task: \"" + str(task) + "\"")
        conn.close()

    @todo.command(usage="<task number>")
    async def remove(self, ctx, task_number: int):
        '''
        Removes a task from your to-do list.
        w.todo remove <task number>
        '''
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT todo_list FROM users
                    WHERE ID = %s; """, (str(ctx.author.id), ))
        todo_list = c.fetchone()[0]
        if todo_list is None:
            await ctx.send("Your to-do list is empty! You can add a task with \"w.todo add <task>\".")
        elif 1 <= task_number <= len(todo_list):
            task_to_remove = todo_list[task_number-1]
            c.execute(""" UPDATE users
                        SET todo_list = array_remove(todo_list, %s)
                        WHERE ID = %s; """, (task_to_remove, str(ctx.author.id)))
            conn.commit()
            await ctx.send("Removed task: \"" + task_to_remove + "\"")
        else:
            await ctx.send("You must input <task number> as an integer between 1 and " + str(len(todo_list)))
        conn.close()

    @todo.command(usage="<task number>")
    async def check(self, ctx, task_number: int):
        '''
        Checks or unchecks a task from your to-do list.
        w.todo check <task number>
        '''
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT todo_list FROM users
                    WHERE ID = %s; """, (str(ctx.author.id), ))
        todo_list = c.fetchone()[0]
        if todo_list is None:
            await ctx.send("Your to-do list is empty! You can add a task with \"w.todo add <task>\".")
        elif 1 <= task_number <= len(todo_list):
            task_to_check = todo_list[task_number-1]
            if task_to_check[:2] == "~~" and task_to_check[-2:] == "~~":
                c.execute(""" UPDATE users
                            SET todo_list = array_replace(todo_list, %s, %s)
                            WHERE ID = %s; """, (task_to_check, task_to_check[2:-2], str(ctx.author.id)))
                conn.commit()
                await ctx.send("Unchecked task: \"" + task_to_check[2:-2] + "\"")
            else:
                c.execute(""" UPDATE users
                            SET todo_list = array_replace(todo_list, %s, %s)
                            WHERE ID = %s; """, (task_to_check, "~~"+task_to_check+"~~", str(ctx.author.id)))
                conn.commit()
                await ctx.send("Checked task: \"" + task_to_check + "\"")
        else:
            await ctx.send("You must input <task number> as an integer between 1 and " + str(len(todo_list)))
        conn.close()

    @remove.error
    @check.error
    async def todo_error(self, ctx, error):
        if isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You must input the <task number> as an integer!")
        else:
            await ctx.send("Unknown error. Please tell Willa.")
            print(error)

    @todo.command(usage="<task number> <new task number>")
    async def move(self, ctx, task_number: int, new_task_number: int):
        '''
        Moves a task to a new location on the list.
        w.todo move <task number> <new task number>
        '''
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        c.execute(""" SELECT todo_list FROM users
                    WHERE ID = %s; """, (str(ctx.author.id), ))
        todo_list = c.fetchone()[0]
        if todo_list is None:
            await ctx.send("Your to-do list is empty! You can add a task with \"w.todo add <task>\".")
        elif 1 <= task_number <= len(todo_list) and 1 <= new_task_number <= len(todo_list)+1:
            task_to_move = todo_list[task_number-1]
            if task_number < new_task_number:
                todo_list.insert(new_task_number, task_to_move)
                todo_list.remove(task_to_move)
                c.execute(""" UPDATE users
                            SET todo_list = %s
                            WHERE ID = %s; """, (todo_list, str(ctx.author.id)))
                conn.commit()
                await ctx.send(f"Moved task: \"{task_to_move}\" to number {new_task_number} on the list")
            elif task_number > new_task_number:
                todo_list.remove(task_to_move)
                todo_list.insert(new_task_number-1, task_to_move)
                c.execute(""" UPDATE users
                            SET todo_list = %s
                            WHERE ID = %s; """, (todo_list, str(ctx.author.id)))
                conn.commit()
                await ctx.send(f"Moved task: \"{task_to_move}\" to number {new_task_number} on the list")
            else:
                await ctx.send(f"Task is already in number {new_task_number} on the list!")
        elif 1 <= task_number <= len(todo_list):
            await ctx.send("You must input <new task number> as an integer between 1 and " + str(len(todo_list)+1))
        else:
            await ctx.send("You must input <task number> as an integer between 1 and " + str(len(todo_list)))
        conn.close()

    @move.error
    async def todo_error(self, ctx, error):
        if isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You must input the <task number> and <new task number> as integers!")
        else:
            await ctx.send("Unknown error. Please tell Willa.")
            print(error)

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
        conn.commit()
        await ctx.send("Your to-do list has been cleaned.")
        conn.close()


def setup(bot):
    bot.add_cog(Todo(bot))