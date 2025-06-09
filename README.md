# Documentação da Plataforma SecretPhotos

## Visão Geral

SecretPhotos é uma aplicação web desenvolvida em Flask (Python) que permite aos usuários esconder mensagens de texto secretas dentro de imagens e, posteriormente, extrair essas mensagens. A plataforma utiliza técnicas de esteganografia para incorporar o texto nos pixels da imagem de forma que a alteração seja visualmente imperceptível.

## Funcionalidades

A interface da aplicação é dividida em duas abas principais:

1.  **Esconder Texto**:
    *   Permite ao usuário fazer upload de uma imagem (formatos suportados: PNG, JPG, JPEG).
    *   Permite ao usuário inserir um texto secreto a ser escondido na imagem.
    *   Processa a imagem, incorporando o texto secreto.
    *   Exibe a imagem processada e oferece um botão para download da mesma.
    *   Mostra uma galeria de imagens previamente enviadas, que podem ser selecionadas para novas operações.

2.  **Extrair Texto**:
    *   Permite ao usuário fazer upload de uma imagem que contenha um texto oculto (formatos suportados: PNG, JPG, JPEG).
    *   Alternativamente, o usuário pode selecionar uma imagem da galeria de uploads ou uma imagem previamente processada (se ainda estiver disponível no servidor).
    *   Processa a imagem e extrai o texto secreto.
    *   Exibe o texto extraído.

Além disso, a plataforma conta com as seguintes funcionalidades:

*   **Galeria de Imagens Anteriores**: Exibe as imagens que foram enviadas pelo usuário na sessão atual, facilitando a reutilização.
*   **Limpar Todas as Imagens**: Um botão que permite ao usuário remover todas as imagens enviadas e processadas do servidor.
*   **Download da Imagem Processada**: Após esconder um texto, o usuário pode baixar a imagem resultante.

## Como Funciona a Esteganografia Aplicada (`tools.py`)

O módulo `tools.py` é o coração da funcionalidade de esteganografia da plataforma. Ele utiliza o método LSB (Least Significant Bit - Bit Menos Significativo) para esconder e extrair texto das imagens.

### Funções Principais em `tools.py`:

1.  **`str_to_bin(text)`**:
    *   **Objetivo**: Converter uma string de texto em sua representação binária.
    *   **Funcionamento**: Cada caractere da string é convertido para seu valor ASCII e, em seguida, para uma representação binária de 8 bits. Todos os bits são concatenados para formar uma única string binária.

2.  **`bin_to_str(binary)`**:
    *   **Objetivo**: Converter uma string binária de volta para texto.
    *   **Funcionamento**: A string binária é dividida em blocos de 8 bits. Cada bloco é convertido para seu valor inteiro correspondente, que por sua vez é convertido de volta para o caractere ASCII.

3.  **`hide_text_in_image(image_path, output_path, secret_text)`**:
    *   **Objetivo**: Esconder uma mensagem de texto secreta dentro de uma imagem.
    *   **Funcionamento**:
        1.  A imagem é aberta e convertida para o formato RGB (para garantir que cada pixel tenha componentes de cor Vermelho, Verde e Azul).
        2.  O texto secreto é primeiro convertido para sua representação binária usando `str_to_bin`.
        3.  Um **delimitador de fim de mensagem** (`1111111111111110`, que são dois bytes, FF FE em hexadecimal, improváveis de ocorrer naturalmente em texto comum) é anexado à string binária do texto. Isso é crucial para saber onde o texto secreto termina durante o processo de extração.
        4.  A função itera sobre os pixels da imagem, um por um, e para cada pixel, modifica o bit menos significativo (LSB) de cada um dos seus componentes de cor (R, G, B) para armazenar sequencialmente os bits da mensagem binária.
            *   Por exemplo, se o LSB do componente Vermelho de um pixel é `0` e o bit da mensagem a ser escondido é `1`, o LSB do Vermelho é alterado para `1`. Se já for `1` e o bit da mensagem for `1`, ele permanece `1`. A operação `(componente & ~1) | bit_mensagem` garante isso.
        5.  Este processo continua até que todos os bits da mensagem (incluindo o delimitador) sejam armazenados.
        6.  A imagem modificada é salva no caminho de saída especificado.

4.  **`extract_text_from_image(image_path)`**:
    *   **Objetivo**: Extrair uma mensagem de texto secreta de uma imagem.
    *   **Funcionamento**:
        1.  A imagem é aberta e convertida para o formato RGB.
        2.  A função itera sobre os pixels da imagem, da mesma forma que na função de esconder.
        3.  Para cada componente de cor (R, G, B) de cada pixel, o LSB é extraído (`componente & 1`).
        4.  Esses bits extraídos são concatenados para reconstruir a string binária que foi escondida.
        5.  A função procura pelo delimitador de fim de mensagem (`1111111111111110`) na string binária reconstruída.
        6.  Se o delimitador for encontrado, todos os bits até o início do delimitador são considerados como a mensagem secreta. Essa porção da string binária é então convertida de volta para texto usando `bin_to_str`.
        7.  Se o delimitador não for encontrado, significa que a imagem pode não conter uma mensagem escondida com este método, ou que a mensagem está corrompida.


## Estrutura do Projeto

*   `app.py`: Arquivo principal da aplicação Flask, contém as rotas e a lógica de manipulação das requisições.
*   `tools.py`: Módulo com as funções de esteganografia.
*   `static/`: Pasta para arquivos estáticos.
    *   `uploads/`: Armazena as imagens originais enviadas pelos usuários.
    *   `processed/`: Armazena as imagens que tiveram texto ocultado.
*   `templates/`: Contém os templates HTML.
    *   `index.html`: Template principal da interface do usuário.
*   `README.md`: Este arquivo de documentação.

## Como Executar a Aplicação

1.  Certifique-se de ter Python e pip instalados.
2.  Clone o repositório (ou tenha os arquivos do projeto).
3.  Instale as dependências:
    ```powershell
    pip install -r requirements.txt
    ```
4.  Execute a aplicação:
    ```powershell
    python app.py
    ```
5.  Abra seu navegador e acesse `http://127.0.0.1:5000/`.
