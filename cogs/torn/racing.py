"""
Copyright © Dennisjr13 2025-Present - https://github.com/dennisjr13
Description:
A cog for Torn Racing-related requests
"""

import requests
from discord.ext import commands
from discord.ext.commands import Context
from table2ascii import table2ascii as t2a, PresetStyle


class Racing(commands.Cog, name="racing"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="myracingskill",
        description="Returns the racing skill of all faction members.",
    )
    async def myracingskill(self, context: Context) -> None:
        # Extract the Torn member_id
        member_id = context.author.display_name[context.author.display_name.index("[") + 1:context.author.display_name.index("]")]

        # TODO: get just member_id's racing skill
        print(member_id)

    @commands.hybrid_command(
        name="allracingskill",
        description="Returns the racing skill of all Night's Watch faction members.",
    )
    async def allracingskill(self, context: Context) -> None:
        """
        Returns the racing skill of all faction members.

        :param context: The application command context.
        """
        key = self.bot.tornstats_api_key

        # Read in roster info (for name)
        roster_url = 'https://www.tornstats.com/api/v2/{}/faction/roster/'.format(key)
        roster_request = requests.get(roster_url)
        roster_data = roster_request.json()

        # Read in roster skills (for member_id and racing_skill)
        skills_url = 'https://www.tornstats.com/api/v2/{}/faction/skills/'.format(key)
        skills_request = requests.get(skills_url)
        skills_data = skills_request.json()

        # Extract members from each JSON
        skills_members = skills_data['members']
        roster_members = roster_data.get('members', {})

        table_data = []
        for member_id, skills in skills_members.items():
            racing_skill = skills.get('racing', 0)
            name = roster_members.get(member_id, {}).get('name', 'Unknown')
            table_data.append([name, racing_skill])

        # sort by racing skill
        table_data.sort(reverse=True, key=lambda skill_lvl: skill_lvl[1])

        # convert racing skill to string with 2 decimal places
        for row in table_data:
            row[1] = f"{row[1]:.2f}"

        output = t2a(
            header=['Name', 'Racing'],
            body=table_data,
            style=PresetStyle.thin_compact,
            cell_padding=0,
        )

        await context.send(f"```\n{output}\n```")

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Racing(bot))
