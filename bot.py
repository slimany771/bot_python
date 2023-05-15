import discord
from discord.ext import commands
from datetime import datetime

# Création des intents pour le bot
intents = discord.Intents.all()

# Création de l'objet bot avec le préfixe de commande et les intents
client = commands.Bot(command_prefix="!", intents=intents)

# Classe pour représenter un nœud dans la liste chaînée
class CommandNode:
    def __init__(self, command, author, timestamp):
        self.command = command
        self.author = author
        self.timestamp = timestamp
        self.next = None
        self.prev = None

# Classe pour représenter la liste chaînée d'historique des commandes
class CommandHistory:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current_node = None

    def add_command(self, command, author):
        timestamp = datetime.now()
        node = CommandNode(command, author, timestamp)
        if self.head is None:
            self.head = node
            self.tail = node
            self.current_node = node
        else:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node

    def get_latest_command(self):
        if self.tail is None:
            return None
        return self.tail.command

    def get_user_commands(self, author):
        user_commands = []
        current_node = self.head
        while current_node is not None:
            if current_node.author == author:
                user_commands.append(current_node.command)
            current_node = current_node.next
        return user_commands
    
    def move_to_previous_command(self):
        if self.current_node is None or self.current_node.prev is None:
            return None
        self.current_node = self.current_node.prev
        return self.current_node.command
    
    def move_to_next_command(self):
        if self.current_node is None or self.current_node.next is None:
            return None
        self.current_node = self.current_node.next
        return self.current_node.command
    
    def clear_history(self):
        self.head = None
        self.tail = None
        self.current_node = None

# Historique global des commandes
history = CommandHistory()

# Commande Delete -> Supprimer les messages en masse(limitation à 10)
@client.command(name="delete")
async def delete(ctx):
    await ctx.channel.purge(limit=10)

# Commande Bot -> Info sur le BOT 
@client.command(name="bot")
async def bot_info(ctx):
    description = "lacrim-bot à votre service pour vous aider à devenir de véritables Hommes !"
    version = "1.0.0"
    developpeur = "Esteban PDG"

    embed = discord.Embed(title="Informations sur le bot", color=discord.Color.blue())
    embed.add_field(name="Description", value=description, inline=False)
    embed.add_field(name="Version", value=version, inline=False)
    embed.add_field(name="Développeur", value=developpeur, inline=False)

    await ctx.send(embed=embed)


########################
######################## 
# Commande SONDAGE 
@client.command(name="sondage")
async def create_poll(ctx, question, *options):
    # Vérifier que le nombre d'options est valide
    if len(options) < 2 or len(options) > 10:
        await ctx.send("Le sondage doit avoir entre 2 et 10 options.")
        return

    # Créer le message du sondage
    poll_message = f"**Sondage : {question}**\n\n"
    for i, option in enumerate(options, start=1):
        poll_message += f"{i}. {option}\n"

    # Envoyer le message du sondage
    poll = await ctx.send(poll_message)

    # Ajouter les réactions pour voter sur les options
    for i in range(len(options)):
        await poll.add_reaction(f"{i+1}\N{COMBINING ENCLOSING KEYCAP}")

    await ctx.message.delete()  # Supprimer la commande du sondage

    # Répondre avec un message confirmant la création du sondage
    await ctx.send("Le sondage a été créé ! Utilisez les réactions pour voter !")

########################
######################## 


# Commande History -> Afficher historique de commande 
@client.command(name="history")
async def show_history(ctx):
    latest_command = history.get_latest_command()
    if latest_command is None:
        await ctx.send("Aucune commande dans l'historique.")
    else:
        embed = discord.Embed(title="Historique des commandes", color=discord.Color.blue())
        embed.add_field(name="Dernière commande rentrée", value=latest_command, inline=False)
        await ctx.send(embed=embed)


# Commande Clear_History -> Vide l'historique de commande 
@client.command(name="clear_history")
async def clear_history(ctx):
    history.clear_history()
    
    description = "L'historique des commandes a été vidé."
    
    embed = discord.Embed(title="Action effectuée", description=description, color=discord.Color.green())
    
    await ctx.send(embed=embed)


# Commande Prev -> Afficher Precedente commande dans l'historique
@client.command(name="prev")
async def move_to_previous_command(ctx):
    command = history.move_to_previous_command()
    if command is None:
        await ctx.send("Il n'y a pas de commande précédente dans l'historique.")
    else:
        embed = discord.Embed(title="Commande précédente", description=command, color=discord.Color.blue())
        await ctx.send(embed=embed)


# Commande Next -> Afficher Suivante commande dans l'historique 
@client.command(name="next")
async def move_to_next_command(ctx):
    command = history.move_to_next_command()
    if command is None:
        await ctx.send("Il n'y a pas de commande suivante dans l'historique.")
    else:
        embed = discord.Embed(title="Commande suivante", description=command, color=discord.Color.blue())
        await ctx.send(embed=embed)


# Commande User History -> Afficher l'Historique d'un utilisateur 
@client.command(name="user_history")
async def show_user_history(ctx, user: discord.User):
    user_commands = history.get_user_commands(user)
    if not user_commands:
        embed = discord.Embed(
            title=f"Historique des commandes de l'utilisateur {user.name}",
            description="Aucune commande de cet utilisateur dans l'historique.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        command_list = "\n".join(user_commands)
        embed = discord.Embed(
            title=f"Historique des commandes de l'utilisateur {user.name}",
            description=command_list,
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

# Ajouter Commande à l'historique 
@client.event
async def on_command_completion(ctx):
    command = ctx.message.content
    author = ctx.message.author
    history.add_command(command, author)

# Est entrain d'écrire 
@client.event
async def on_typing(channel, user, when):
    embed = discord.Embed(title="En train d'écrire", color=discord.Color.orange())
    embed.add_field(name="Utilisateur", value=user.name, inline=False)
    embed.add_field(name="Statut", value="En train d'écrire...", inline=False)
    await channel.send(embed=embed)


# Définition d'un événement pour quand le bot est prêt
@client.event
async def on_ready():
    print("Lacrim est prêt !")

# Définition d'un événement lorsqu'un utilisateur rejoins le serveur 
@client.event
async def on_member_join(member):
    general_channel = client.get_channel(1091342192070643732)

    description = f"Lacrim-bot t'accueil sur le Serveur {member.name} !"
    embed = discord.Embed(title="Bienvenue", description=description, color=discord.Color.blue())

    await general_channel.send(embed=embed)


########################
######################## 
#  Discussion Bot
class Node:
    def __init__(self, question, yes_node=None, no_node=None):
        self.question = question
        self.yes_node = yes_node
        self.no_node = no_node

# Construction de l'arbre binaire pour le questionnaire
root = Node("N'oublie jamais que Lacrim a dit : Mon frère si t'as le cœur froid, t'iras bronzer en enfer. Es-tu d'accord ?",
            yes_node=Node("Veux-tu une autre citation ?",
                          yes_node=Node("Mieux vaut un ennemi qu'un ami qui m'envie. Gang ou pas en sah ?"),
                          no_node=Node("Aimes-tu lacrim ?")),
            no_node=Node("Es-tu sur d'aimer LACRIM ?"))

conversation_active = False
current_node = root

@client.command(name="start_conversation")
async def start_conversation(ctx):
    global conversation_active, current_node
    if conversation_active:
        await ctx.send("Une conversation est déjà en cours. Utilisez la commande !reset pour recommencer.")
    else:
        conversation_active = True
        current_node = root
        
        embed = discord.Embed(title="Conversation avec Lacrim", color=discord.Color.blue())
        embed.description = current_node.question

        await ctx.send(embed=embed)

@client.command(name="reset")
async def reset_conversation(ctx):
    global conversation_active, current_node
    if not conversation_active:
        await ctx.send("Aucune conversation en cours. Utilisez la commande !start_conversation pour commencer.")
    else:
        conversation_active = False
        current_node = root

        embed = discord.Embed(title="Conversation réinitialisée", color=discord.Color.blue())
        await ctx.send(embed=embed)

@client.event
async def on_message(message):
    global conversation_active, current_node

    if message.author == client.user:
        return

    if conversation_active:
        if message.content.lower() == "oui":
            if current_node.yes_node:
                current_node = current_node.yes_node
                await message.channel.send(current_node.question)
            else:
                await message.channel.send("Cela me va droit au coeur, personne sur cette terre n'aime pas LACRIM ! ")
                conversation_active = False
        elif message.content.lower() == "non":
            if current_node.no_node:
                current_node = current_node.no_node
                await message.channel.send(current_node.question)
            else:
                await message.channel.send("Tu mérites le pire pour ce que tu viens de dire !")
                conversation_active = False

    await client.process_commands(message)

########################
######################## 

# Lancement du BOT(ne jamais publier le TOKEN)
client.run("MTA5MTMzNDU4OTExNDQ5MDk0MQ.Gf4yzh.6lv3rLFtI6ZzwLNswb2UmGeCiJuQ8vzTpB0Kk4")