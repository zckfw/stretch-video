# stretch-video

Aplicativo para deixar um vídeo esticado (stretched) na resolução escolhida.

Arraste um vídeo para a janela ou clique para selecioná-lo. Escolha a resolução e clique em **Esticar vídeo**. O resultado é salvo no mesmo caminho do vídeo original, como `nome_stretched.mp4`. Se esse nome já existir, usa `_stretched_2`, `_stretched_3` etc...

## Como usar

Baixe o executável para Windows na [página de releases](https://github.com/zckfw/stretch-video/releases).

O [FFmpeg](https://ffmpeg.org/download.html) precisa estar disponível no `PATH`.

Para executar pelo código-fonte, use Python 3.10+:

```bash
pip install -r requirements.txt
python main.py
```

Interface em Qt; processamento com FFmpeg.
