
[resources](https://github.com/magenta/magenta/tree/master/magenta/models/svg_vae),[example
font](http://www.eaglefonts.com/data/media/326/FG_Jeff.ttf),
[arxiv](https://arxiv.org/abs/1904.02632) 


### TODO/NOTES:

1. the urls.txt is found here (warning, this is an autodownload link)
   [here](https://storage.googleapis.com/magentadata/models/svg_vae/glyphazzn_urls.txt)
   and is found on the magenta github [page](https://github.com/magenta/magenta/tree/master/magenta/models/svg_vae)

2. creating the parquetio dataset requires fontforge fontforge on ubunutu is a
   bit of a pain. I used: 
   ```bash
    sudo apt-get install -y python-fontforge
    ```
    which installs fontforge in the base environment (which for me is
    `/usr/bin/python`)

    so fontforge can be run with:
    ```bash
    /usr/bin/python font_forge.py
    ```

 3. Will need to add more svg commands
    [info](https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths)
 
 4. I'm not using the tfrrecord directory correctly as it seems to only be
    reading the first example in each shard
