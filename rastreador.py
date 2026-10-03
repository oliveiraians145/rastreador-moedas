import requests

def obter_cotacoes():
    try:
        print("Tentando conectar à API...")
        
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=brl&include_24hr_change=true"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        moeda = input('Qual moeda você quer consultar? (bitcoin, ethereum, solana): ')
        consultar_moeda = lambda m: data.get(m, {}).get('brl')
        
        if consultar_moeda(moeda):
            print(f'\nO preço de {moeda} é: R$ {consultar_moeda(moeda):,.2f}')
        else:
            print('\nMoeda não encontrada')
        print(f'\nBitcoin:    R$ {data["bitcoin"]["brl"]:,.2f}  ({data["bitcoin"]["brl_24h_change"]:+.2f}%)')
        print(f'Ethereum:   R$ {data["ethereum"]["brl"]:,.2f}  ({data["ethereum"]["brl_24h_change"]:+.2f}%)')
        print(f'Solana:     R$ {data["solana"]["brl"]:,.2f}  ({data["solana"]["brl_24h_change"]:+.2f}%)')
        
        with open('cotacoes.txt', 'w', encoding='utf-8') as arquivo:
            arquivo.write(f'Bitcoin: R${data["bitcoin"]["brl"]:.2f}\n')
            arquivo.write(f'Ethereum: R${data["ethereum"]["brl"]:.2f}\n')
            arquivo.write(f'Solana: R${data["solana"]["brl"]:.2f}\n')
        
        print('\nCotacoes salvas em cotacoes.txt')
        
    except Exception as e:
        # Se algo der erro, captura e mostra a mensagem
        print(f'Ocorreu um erro: {e}')
obter_cotacoes()  
