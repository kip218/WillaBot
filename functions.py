

def pfp_helper(ctx, user):
    '''
    Sends [user]'s profile picture
    '''
    if user is None:
        member = ctx.message.author
        embed = get_pfp(member)
        await ctx.send(embed=embed)
    elif len(ctx.message.mentions) > 0:
        member = ctx.message.mentions[0]
        embed = get_pfp(member)
        await ctx.send(embed=embed)
    else:
        lst_members = ctx.guild.members
        #loop to search name
        ind = 0
        found = False
        while found == False and ind < len(lst_members):
            curr_member = lst_members[ind]
            if user.lower() in curr_member.display_name.lower():
                embed = get_pfp(curr_member)
                await ctx.send(embed=embed)
                found = True
            elif user.lower() in curr_member.name.lower():
                embed = get_pfp(curr_member)
                await ctx.send(embed=embed)
                found = True
            else:
                ind += 1
        if found == False:
            await ctx.send("Could not find user named \"" + user + "\"")
