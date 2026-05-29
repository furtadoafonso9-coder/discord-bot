import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import timedelta
import json
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Arquivo para armazenar dados
DATA_FILE = "bot_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"tickets": {}, "registros": {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f'{bot.user} foi conectado com sucesso!')
    print(f'ID do Bot: {bot.user.id}')
    try:
        synced = await bot.tree.sync()
        print(f'✅ Sincronizados {len(synced)} comando(s)')
    except Exception as e:
        print(f'❌ Erro ao sincronizar: {e}')

# ===================== COMANDO: BAN =====================
@bot.tree.command(name="ban", description="Banir um usuário do servidor")
@app_commands.describe(usuario="Usuário a ser banido", motivo="Motivo do ban (opcional)")
async def ban(interaction: discord.Interaction, usuario: discord.User, motivo: str = "Sem motivo"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ Você não tem permissão para banir membros!", ephemeral=True)
        return
    
    try:
        await interaction.guild.ban(usuario, reason=motivo)
        embed = discord.Embed(
            title="🔨 Usuário Banido",
            description=f"**Usuário:** {usuario.mention}\n**Motivo:** {motivo}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro ao banir usuário: {str(e)}", ephemeral=True)

# ===================== COMANDO: SILENCIO =====================
@bot.tree.command(name="silencio", description="Silenciar um membro por um tempo determinado")
@app_commands.describe(membro="Membro a silenciar", tempo="Tempo em minutos", motivo="Motivo do mute")
async def silencio(interaction: discord.Interaction, membro: discord.Member, tempo: int, motivo: str = "Sem motivo"):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ Você não tem permissão para silenciar membros!", ephemeral=True)
        return
    
    try:
        duracao = timedelta(minutes=tempo)
        await membro.timeout(duracao, reason=motivo)
        embed = discord.Embed(
            title="🔇 Membro Silenciado",
            description=f"**Membro:** {membro.mention}\n**Tempo:** {tempo} minutos\n**Motivo:** {motivo}",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro ao silenciar membro: {str(e)}", ephemeral=True)

# ===================== COMANDO: ADDTAG =====================
@bot.tree.command(name="addtag", description="Adicionar uma tag/cargo a um usuário")
@app_commands.describe(usuario="Usuário que receberá a tag", tag="Tag/Cargo a adicionar")
async def addtag(interaction: discord.Interaction, usuario: discord.Member, tag: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Você não tem permissão para gerenciar roles!", ephemeral=True)
        return
    
    try:
        await usuario.add_roles(tag)
        embed = discord.Embed(
            title="🏷️ Tag Adicionada",
            description=f"**Usuário:** {usuario.mention}\n**Tag:** {tag.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro ao adicionar tag: {str(e)}", ephemeral=True)

# ===================== COMANDO: QUIT =====================
@bot.tree.command(name="quit", description="Expulsar um usuário do servidor")
@app_commands.describe(usuario="Usuário a expulsar", motivo="Motivo da expulsão (opcional)")
async def quit(interaction: discord.Interaction, usuario: discord.User, motivo: str = "Sem motivo"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ Você não tem permissão para expulsar membros!", ephemeral=True)
        return
    
    try:
        member = interaction.guild.get_member(usuario.id)
        if member:
            await member.kick(reason=motivo)
            embed = discord.Embed(
                title="👢 Usuário Expulso",
                description=f"**Usuário:** {usuario.mention}\n**Motivo:** {motivo}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Usuário não encontrado no servidor!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro ao expulsar usuário: {str(e)}", ephemeral=True)

# ===================== COMANDO: IDDC =====================
@bot.tree.command(name="iddc", description="Ver o ID do Discord de um usuário")
@app_commands.describe(usuario="Usuário para ver o ID")
async def iddc(interaction: discord.Interaction, usuario: discord.User):
    embed = discord.Embed(
        title="🔍 ID do Discord",
        description=f"**Usuário:** {usuario.mention}\n**ID:** `{usuario.id}`",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=usuario.avatar.url if usuario.avatar else None)
    await interaction.response.send_message(embed=embed)

# ===================== COMANDO: RULES =====================
@bot.tree.command(name="rules", description="Enviar as regras do servidor (apenas admins)")
async def rules(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Apenas admins podem enviar as regras!", ephemeral=True)
        return
    
    rules_text = """
🚨 **REGRAS DO SERVIDOR** 🚨

1️⃣ **Respeito** - Trate todos com respeito
2️⃣ **Spam** - Proibido spam ou flood
3️⃣ **Linguagem** - Evite linguagem ofensiva
4️⃣ **Publicidade** - Sem auto-promoção não autorizada
5️⃣ **NSFW** - Conteúdo NSFW é proibido
6️⃣ **Moderação** - Respeite as decisões da moderação

Violações podem resultar em silenciamento, kick ou ban permanente.
    """
    
    embed = discord.Embed(
        title="📋 Regras do Servidor",
        description=rules_text,
        color=discord.Color.gold()
    )
    embed.set_footer(text="Leia com atenção!")
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Regras enviadas!", ephemeral=True)

# ===================== COMANDO: LOCK =====================
@bot.tree.command(name="lock", description="Trancar um canal (apenas admins podem escrever)")
async def lock(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ Você não tem permissão para trancar canais!", ephemeral=True)
        return
    
    try:
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        embed = discord.Embed(
            title="🔒 Canal Trancado",
            description="Este canal foi trancado. Apenas administradores podem escrever.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro ao trancar canal: {str(e)}", ephemeral=True)

# ===================== COMANDO: UNLOCK =====================
@bot.tree.command(name="unlock", description="Destrancar um canal")
async def unlock(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ Você não tem permissão para destrancar canais!", ephemeral=True)
        return
    
    try:
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        embed = discord.Embed(
            title="🔓 Canal Destranado",
            description="Este canal foi destancado. Todos podem escrever novamente.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro ao destrancar canal: {str(e)}", ephemeral=True)

# ===================== COMANDO: REGISTRO =====================
class RegistroView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(persistent=True)
        self.guild_id = guild_id
    
    @discord.ui.button(label="Registrar", style=discord.ButtonStyle.success)
    async def register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        user_id = str(interaction.user.id)
        
        if user_id in data["registros"]:
            await interaction.response.send_message("❌ Você já se registrou!", ephemeral=True)
            return
        
        data["registros"][user_id] = {
            "username": interaction.user.name,
            "status": "pendente",
            "guild_id": self.guild_id
        }
        save_data(data)
        
        await interaction.response.send_message("✅ Seu registro foi enviado para aprovação!", ephemeral=True)
        
        guild = bot.get_guild(self.guild_id)
        admin_channel = discord.utils.get(guild.channels, name="admin-logs")
        
        if not admin_channel:
            admin_channel = guild.text_channels[0]
        
        aprovacao_view = AprovacaoView(interaction.user.id, interaction.user.name)
        embed = discord.Embed(
            title="📝 Novo Registro para Aprovação",
            description=f"**Usuário:** {interaction.user.mention}\n**Username:** {interaction.user.name}",
            color=discord.Color.yellow()
        )
        await admin_channel.send(embed=embed, view=aprovacao_view)

class AprovacaoView(discord.ui.View):
    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
    
    @discord.ui.button(label="✅ Aprovar", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Apenas admins podem aprovar!", ephemeral=True)
            return
        
        data = load_data()
        user_id = str(self.user_id)
        
        if user_id in data["registros"]:
            data["registros"][user_id]["status"] = "aprovado"
            save_data(data)
        
        user = await bot.fetch_user(self.user_id)
        try:
            embed = discord.Embed(
                title="✅ Registro Aprovado!",
                description="Seu registro foi aprovado com sucesso!",
                color=discord.Color.green()
            )
            await user.send(embed=embed)
        except:
            pass
        
        await interaction.response.send_message(f"✅ Registro de {self.username} aprovado!", ephemeral=True)
        await interaction.message.delete()
    
    @discord.ui.button(label="❌ Rejeitar", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Apenas admins podem rejeitar!", ephemeral=True)
            return
        
        data = load_data()
        user_id = str(self.user_id)
        
        if user_id in data["registros"]:
            del data["registros"][user_id]
            save_data(data)
        
        user = await bot.fetch_user(self.user_id)
        try:
            embed = discord.Embed(
                title="❌ Registro Rejeitado",
                description="Seu registro foi rejeitado.",
                color=discord.Color.red()
            )
            await user.send(embed=embed)
        except:
            pass
        
        await interaction.response.send_message(f"❌ Registro de {self.username} rejeitado!", ephemeral=True)
        await interaction.message.delete()

@bot.tree.command(name="registro", description="Criar página de registro para membros")
async def registro(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Apenas admins podem criar registros!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📝 Registro de Membro",
        description="Clique no botão abaixo para se registrar no servidor.",
        color=discord.Color.blue()
    )
    
    view = RegistroView(interaction.guild.id)
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Página de registro criada!", ephemeral=True)

# ===================== COMANDO: TICKET =====================
class TicketView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(persistent=True)
        self.guild_id = guild_id
    
    @discord.ui.button(label="📩 Abrir Ticket", style=discord.ButtonStyle.primary)
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        guild = bot.get_guild(self.guild_id)
        
        ticket_category = discord.utils.get(guild.categories, name="Tickets")
        if not ticket_category:
            ticket_category = await guild.create_category("Tickets")
        
        channel_name = f"ticket-{interaction.user.name}"
        ticket_channel = await guild.create_text_channel(
            channel_name,
            category=ticket_category
        )
        
        await ticket_channel.set_permissions(interaction.guild.default_role, view_channel=False)
        await ticket_channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
        
        admin_role = discord.utils.find(lambda r: r.name == "Admin" or r.permissions.administrator, guild.roles)
        if admin_role:
            await ticket_channel.set_permissions(admin_role, view_channel=True, send_messages=True)
        
        data["tickets"][str(ticket_channel.id)] = {
            "user_id": interaction.user.id,
            "username": interaction.user.name,
            "status": "aberto"
        }
        save_data(data)
        
        embed = discord.Embed(
            title="🎫 Novo Ticket",
            description=f"Bem-vindo, {interaction.user.mention}!\n\nDescreva seu problema ou dúvida abaixo.",
            color=discord.Color.blue()
        )
        
        close_view = TicketCloseView(ticket_channel.id)
        await ticket_channel.send(embed=embed, view=close_view)
        
        await interaction.response.send_message(f"✅ Ticket criado: {ticket_channel.mention}", ephemeral=True)

class TicketCloseView(discord.ui.View):
    def __init__(self, channel_id):
        super().__init__()
        self.channel_id = channel_id
    
    @discord.ui.button(label="❌ Fechar Ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        channel_id = str(self.channel_id)
        
        if channel_id in data["tickets"]:
            data["tickets"][channel_id]["status"] = "fechado"
            save_data(data)
        
        channel = bot.get_channel(self.channel_id)
        if channel:
            await channel.delete()

@bot.tree.command(name="ticket", description="Criar sistema de tickets")
async def ticket(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Apenas admins podem criar sistema de tickets!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🎫 Sistema de Tickets",
        description="Clique no botão abaixo para abrir um ticket.\n\nUse tickets para reportar problemas ou tirar dúvidas com a administração.",
        color=discord.Color.purple()
    )
    
    view = TicketView(interaction.guild.id)
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Sistema de tickets criado!", ephemeral=True)

@bot.tree.command(name="ping", description="Verificar se o bot está online")
async def ping(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latência: {round(bot.latency * 1000)}ms",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

def main():
    token = os.getenv('TOKEN')
    if not token:
        print("❌ ERRO: TOKEN não encontrado! Adicione o TOKEN no arquivo .env")
        return
    bot.run(token)

if __name__ == "__main__":
    main()
