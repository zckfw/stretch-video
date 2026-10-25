# stretch-video

Aplicativo simples para esticar um vídeo até a resolução escolhida, sem manter a proporção original.

Arraste um vídeo para a janela ou clique na área central para selecioná-lo. Escolha a largura e a altura e clique em **Criar vídeo**. O resultado é salvo ao lado do original como `nome_stretched.mp4`. Se esse nome já existir, o aplicativo usa `_stretched_2`, `_stretched_3` e assim por diante. O vídeo original não é alterado.

## Como usar

Requer Python 3.10+ e [FFmpeg](https://ffmpeg.org/download.html) disponível no `PATH`.

```bash
pip install -r requirements.txt
python main.py
```

Interface em Qt; processamento com FFmpeg.
