# navyplot

Download navy federal credit card data in CSV format, and make a plot vioa python3.

# Setup

I use Centos 7 with virtual environments like this:

```bash
sudo yum install -y python36-virtualenv
virtualenv-3 venv
source venv/bin/activate
```

Regardless of your python3 environment. install dependencies:

```bash
pip install -r requirements.txt
```

I use an ffmpeg backend. You might change the code around `FuncAnimation` to use imagemagick or whatever.

I install ffmpeg on centos 7 like this:

```bash
sudo yum -y install http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm
```

I edit `/etc/yum.repos.d/nux-dextop.repo` to set `enabled=0`. Then I install ffmpeg like this:

```bas
sudo yum install --enablerepo=nux-dextop -y ffmpeg
```

# Run

First, copy all `*.CSV` files downloaded from navy federal into a local folder `data/`.

Then run:

```bash
# for video
python stitch.py -v
# for image
python stitch.py
```


