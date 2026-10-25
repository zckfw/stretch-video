# stretch-video

Aplicativo para deixar um vídeo esticado (stretched) na reoslução escolhida.

Arraste um vídeo para a janela ou clique para selecioná-lo. Escolha a resolução e clique em **Esticar vídeo**. O resultado é salvo no mesmo caminho do vídeo original, como `nome_stretched.mp4`. Se esse nome já existir, usa `_stretched_2`, `_stretched_3` etc...

## Como usar

Requer Python 3.10+ e [FFmpeg](https://ffmpeg.org/download.html) disponível no `PATH`.

```bash
pip install -r requirements.txt
python main.py
```

Interface em Qt; processamento com FFmpeg.
