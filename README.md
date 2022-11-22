## Problemas conhecidos
- Caso seja executada no Windows, o limite da rede artificial é de 2 nós (pois o sistema impede a abertura de portas adicionais).
- Caso utilize-se de uma porta aleatória para o nó (inserindo 0 como valor), a rede pode apresentar comportamento imprevisível, pois recebe pacotes indesejados de outros programas que rompem com a lógica da implementação.

## Ambiente utilizado
- Python 3.10.8
- Linux (kernel 6.0.8-1-default)

## Instruções
- Executando `python src/main.py` para obter um terminal interativo:
  - Comando `echo`: Uma mensagem percorre toda a DHT e volta ao nó original.
  - Comando `print`: Imprime o conteúdo de cada nó sem acessar a DHT.
  - Comando `find <índice da música> <índice do pedaço>`: Imprime um boolean dizendo se o pedaço com o índice fornecido da música fornecida está presente em algum nó da DHT.
  - Comando `put <índice da música>`: Armazena a música fornecida na DHT.
  - Comando `get <índice da música> <caminho para salvar o arquivo>`: Transfere a música na DHT equivalente à fornecida, armazenando-a no caminho fornecido.
  - Comando `count [std]`: Conta quantos pedaços cada nó possui e os imprime em uma lista. Caso o sub-comando `std` seja fornecido, imprime o desvio padrão da quantidade de pedaços. Não interage com a DHT.
- Pode-se também interagir com os testes no arquivo `src/data.ipynb` via Jupyter Notebook.
