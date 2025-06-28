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
        description="Returns your racing skill.",
    )
    async def myracingskill(self, context: Context) -> None:
        """
        Returns the racing skill of the author.

        :param context: The application command context.
        """
        # Extract the author's Torn name
        torn_name = context.author.display_name[:context.author.display_name.index("[") - 1]

        racing_skill = 0.0
        for index, row in enumerate(self.get_faction_racing_skill()):
            if row[0] == torn_name:
                racing_skill = f"{row[1]:.2f}"
                break

        await context.reply(f"Hi {context.author.display_name}, your racing skill is: {racing_skill}")

    @commands.hybrid_command(
        name="factionracingskill",
        description="Returns the racing skill of all faction members.",
    )
    async def factionracingskill(self, context: Context) -> None:
        """
        Returns the racing skill of all faction members.

        :param context: The application command context.
        """
        table_data = self.get_faction_racing_skill()

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

        await context.author.send(f"```\n{output}\n```")
        await context.reply(
            f"Hi {context.author.display_name}, I've sent you a DM with the racing skills of all Night's Watch members.")

    def get_faction_racing_skill(self) -> list:
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

        return table_data

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Racing(bot))
