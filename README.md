# wallpaper-engine-win

- 简介

  [ffmpeg 下载地址](https://ffmpeg.org/download.html) ，[下载教程](https://blog.csdn.net/weixin_40986713/article/details/135015461)，下载后放根目录即可：

  ```sh
  video-check
    - ffmpeg
      - bin
        - ffmpeg.exe
    - main.py
  ```

- `ui` 库

  `Tkinter` 是标准库的一部分，因此一般情况下不需要单独安装，运行找不到就安装下。

  ```sh
  $ pip install tk
  ```

- 打包

  - 打包插件安装

    ```sh
    $ pip install pyinstaller
    ```

  - 打包指令

    ```sh
    $ pyinstaller --onefile --windowed --noconsole --icon=icon.ico --add-data "icon.ico;." --add-data "ffmpeg;ffmpeg" --name "VideoCheck" main.py
    ```

  - 本地启动

    ```sh
    $ python main.py
    ```
