import os
import re
import asyncio
from telethon import TelegramClient, events

# ====== CONFIGURACOES ======
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ID_AFILIADO = os.getenv("ID_AFILIADO", "cl20260628092446")

CANAL_ORIGEM = "@pcdofafapromo"
CANAL_DESTINO = "@ofertasrelampagotech"

# ====== CLIENTE ======
bot = TelegramClient("bot_ofertas", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ====== FUNCOES ======
def adicionar_afiliado(link):
    sep = "&" if "?" in link else "?"
    return f"{link}{sep}partner_id={ID_AFILIADO}"

def processar_links_texto(texto):
    if not texto:
        return texto
    padrao = r'https?://[^\s)]+mercadolivre[^\s)]+'
    links = re.findall(padrao, texto)
    for link in links:
        texto = texto.replace(link, adicionar_afiliado(link))
    return texto

def processar_entidades(texto, entidades):
    if not entidades or not texto:
        return texto
    for entity in entidades:
        if entity.url and "mercadolivre" in entity.url:
            link_novo = adicionar_afiliado(entity.url)
            texto = texto.replace(entity.url, link_novo)
    return texto

# ====== HANDLER ======
@bot.on(events.NewMessage(chats=CANAL_ORIGEM))
async def encaminhar_oferta(event):
    try:
        texto = event.message.text or ""
        texto = processar_links_texto(texto)
        texto = processar_entidades(texto, event.message.entities)

        if event.message.media:
            await bot.send_message(
                CANAL_DESTINO,
                texto,
                file=event.message.media,
                parse_mode="html"
            )
        else:
            await bot.send_message(
                CANAL_DESTINO,
                texto,
                parse_mode="html"
            )

        print(f"OK - Copiado: {event.message.id}")
    except Exception as erro:
        print(f"ERRO: {erro}")

# ====== INICIAR ======
async def main():
    print("=" * 40)
    print("Bot de Ofertas iniciado!")
    print(f"Origem: {CANAL_ORIGEM}")
    print(f"Destino: {CANAL_DESTINO}")
    print("=" * 40)
    await bot.run_until_disconnected()

asyncio.run(main())
