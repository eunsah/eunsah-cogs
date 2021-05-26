import discord
from redbot.core import commands
from random import choice

kill_list= [
        ('{killer} shoves a double barreled shotgun into {victim}\'s mouth and squeezes the trigger of the gun, causing {victim}\'s head to horrifically explode like a ripe pimple, splattering the young person\'s brain matter, gore, and bone fragments all over the walls and painting it a crimson red.'),
        ('Screaming in sheer terror and agony, {victim} is horrifically dragged into the darkness by unseen forces, leaving nothing but bloody fingernails and a trail of scratch marks in the ground from which the young person had attempted to halt the dragging process.'),
        ('{killer} takes a machette and starts hacking away on {victim}, chopping {victim} into dozens of pieces.'),
        ('{killer} pours acid over {victim}. *"Well don\'t you look pretty right now?"*'),
        ('{victim} screams in terror as a giant creature with huge muscular arms grab {victim}\'s head; {victim}\'s screams of terror are cut off as the creature tears off the head with a sickening crunching sound. {victim}\'s spinal cord, which is still attached to the dismembered head, is used by the creature as a makeshift sword to slice a perfect asymmetrical line down {victim}\'s body, causing the organs to spill out as the two halves fall to their) respective sides.'),
        ('{killer} grabs {victim}\'s head and tears it off with superhuman speed and efficiency. Using {victim}\'s head as a makeshift basketball, {killer} expertly slams dunk it into the basketball hoop, much to the applause of the audience watching the gruesome scene.'),
        ('{killer} uses a shiv to horrifically stab {victim} multiple times in the chest and throat, causing {victim} to gurgle up blood as the young person horrifically dies.'),
        ('{victim} screams as {killer} lifts {victim} up using his superhuman strength. Before {victim} can even utter a scream of terror, {killer} uses his superhuman strength to horrifically tear {victim} into two halves; {victim} stares at the monstrosity in shock and disbelief as {victim} gurgles up blood, the upper body organs spilling out of the dismembered torso, before the eyes roll backward into the skull.'),
        ('{victim} steps on a land mine and is horrifically blown to multiple pieces as the device explodes, the {victim}\'s entrails and gore flying up and splattering all around as if someone had thrown a watermelon onto the ground from the top of a multiple story building.'),
        ('{victim} is killed instantly as the top half of his head is blown off by a Red Army sniper armed with a Mosin Nagant, {victim}\'s brains splattering everywhere in a horrific fashion.'),
        ]


class Kill(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kill(self, ctx, victim: discord.Member):
        """
            Kills the mentioned victim

            
        """

        msg = " "
        user = ctx.message.author

        if victim.id == self.bot.user.id:
            await ctx.send("I refuse to kill myself!")
            
        elif victim.id == user.id:            
            #await ctx.send("I won\'t let you kill yourself!")
            await ctx.send(choice(kill_list).format(victim = user.display_name, killer = self.bot.user.display_name))

        else:
            await ctx.send(choice(kill_list).format(victim = victim.display_name, killer = user.display_name))
