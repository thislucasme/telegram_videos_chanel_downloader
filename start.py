from telethon.sync import TelegramClient
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Substitua os valores abaixo com suas credenciais
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")
id_canal = os.getenv("CHANNEL_ID")

def criar_pasta_se_nao_existir(nome_pasta):
    if not os.path.exists(nome_pasta):
        os.makedirs(nome_pasta)
        print(f'A pasta "{nome_pasta}" foi criada com sucesso.')
    else:
        print(f'A pasta "{nome_pasta}" já existe.')

async def salvar_mensagens(start_message, end_message):
    with open('historico.txt', 'w') as arquivo:
        arquivo.write("Começou em: {}\n".format(start_message))
        arquivo.write("Terminou em: {}\n".format(end_message))

async def download_videos(channel_id, start_message=0, end_message=None):
    criar_pasta_se_nao_existir("videos")
    async with TelegramClient('session_name', api_id, api_hash) as client:
        # Conecta ao Telegram
        await client.start(phone=phone_number)

        try:
            # Obtém a entidade do canal usando o ID do canal
            channel_entity = await client.get_entity(int(channel_id))

            # Cria a pasta para salvar os vídeos, se não existir
            if not os.path.exists('videos'):
                os.makedirs('videos')

            # Itera sobre as mensagens do canal na ordem inversa (do início para o fim)
            async for message in client.iter_messages(channel_entity, reverse=True):
                # Verifica se a mensagem está dentro do intervalo especificado
                if start_message <= int(message.id):
                    if end_message is None or int(message.id) <= end_message:
                        # Verifica se a mensagem é um vídeo
                        if message.video:
                            # Obtém o nome do arquivo do vídeo
                            video_file_name = os.path.join('videos', f"{message.message}.mp4")
                            
                            # Baixa o vídeo exibindo o progresso
                            await client.download_media(
                                message.video,
                                file=video_file_name,
                                progress_callback=lambda current, total: print(f"Baixando {message.message}: {current}/{total} bytes")
                            )
                            print(f"Vídeo {video_file_name} baixado com sucesso!")
        except Exception as e:
            print("Erro ao baixar os vídeos do canal:", e)

async def count_messages(channel_id):
    async with TelegramClient('session_name', api_id, api_hash) as client:
        # Conecta ao Telegram
        await client.start(phone=phone_number)

        try:
            # Obtém a entidade do canal usando o ID do canal
            channel_entity = await client.get_entity(int(channel_id))

            message_count = await client.get_messages(channel_entity, limit=1)
            return message_count.total

        except Exception as e:
            print("Erro ao contar mensagens do canal:", e)
            return None

async def menu(channel_id):
    print("1. Baixar vídeos")
    print("2. Contar mensagens")
    opcao = int(input("Escolha uma opção: "))
    
    if opcao == 1:
        start_message = int(input("Digite o ID da primeira mensagem do intervalo: "))
        end_message = int(input("Digite o ID da última mensagem do intervalo (ou deixe em branco para baixar a partir da primeira mensagem até a última): ") or "0")
        await salvar_mensagens(start_message, end_message)
        await download_videos(channel_id, start_message, end_message)
    elif opcao == 2:
        message_count = await count_messages(channel_id)
        if message_count is not None:
            print(f"Total de mensagens no canal: {message_count}")
    else:
        print("Opção inválida.")

if __name__ == '__main__':
    channel_id = id_canal  # Substitua pelo ID do canal desejado
    import asyncio
    asyncio.run(menu(channel_id))
