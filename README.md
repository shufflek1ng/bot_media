# bot_media
Simple discord bot for playing youtube music through url or search keywords / playing Portuguese Radio Stations in real time


Instruções de uso:



    1. Comando          Uso           Descrição

      !join            !join         Faz o bot entrar na tua voice channel. Precisas de estar num canal de voz.
      !leave           !leave        Faz o bot sair do canal de voz e limpa a queue desse canal.


2️⃣ Reprodução de música
Comando	Uso	Descrição
!play	!play <YouTube URL ou palavras-chave>	Toca uma música do YouTube. Se o bot já estiver a tocar algo, a música é adicionada à queue.
!skip	!skip	Passa para a próxima música na queue do canal de voz.
!np	!np	Mostra a música que está atualmente a tocar.
!queue	!queue	Mostra a lista de músicas que estão na queue do canal de voz.
!volume	!volume <0-100>	Ajusta o volume da música atual.


3️⃣ Rádio portuguesa
Comando	Uso	Descrição
!radio	!radio <estação>	Toca uma estação de rádio portuguesa em tempo real. Disponível:
- antena1
- antena2
- antena3
- rfm
- cidadefm
- radiocomercial
- m80

Exemplo:

!radio antena1


4️⃣ Parar e limpar
Comando	Uso	Descrição
!stop	!stop	Para a música/rádio atual e limpa a queue do canal.


5️⃣ Regras de uso

Cada voice channel tem sua própria queue, permitindo que vários canais toquem músicas diferentes ao mesmo tempo.

Qualquer utilizador no canal de voz pode adicionar músicas à queue ou usar comandos de controle (!skip, !volume).

O bot só pode estar num canal de voz por servidor ao mesmo tempo. Mas com esta versão, cada canal pode ter seu próprio queue.
