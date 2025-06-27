
anda tidak perlu mencantumkan komentar program yang tidak diperlukan ringkas kode d=sdemikian singkat tapi on point hindari penggunaan icon emote, Buatkan kayak quick launcher main.py yang penting untuk menjalankan program seperti ini dimana saya bisa menjalankan load balancer, server, dan player secara bersamaan. buat ui tombolnya, terserah mekanisme nya gimana

yang jelas khusus untuk server itu kan server.py 8890 jika sudah ada server berjalan auto increment ke 8891 dan seterusnya


```bash
ASUS TUF GAMING A15@ASUSTUF-ALVINZP MINGW64 /d/KULIAH/FP PROGJAR/Runes-SteelFighter-Load Balancer
$ py server.py 8890
[SERVER] Running on port 8890...
[SERVER] Player 0 connected from ('127.0.0.1', 62528)
[SERVER] Player 1 connected from ('127.0.0.1', 62534)
```

```bash
ASUS TUF GAMING A15@ASUSTUF-ALVINZP MINGW64 /d/KULIAH/FP PROGJAR/Runes-SteelFighter-Load Balancer
$ py load_balancer.py
[LOAD BALANCER] Listening on port 8888...
[LOAD BALANCER] Client connected from ('127.0.0.1', 62485)
[LOAD BALANCER] Client connected from ('127.0.0.1', 62494)
[LOAD BALANCER] Client connected from ('127.0.0.1', 62527)
[LOAD BALANCER] Client connected from ('127.0.0.1', 62533)
[LOAD BALANCER] Client connected from ('127.0.0.1', 62541)
[LOAD BALANCER] Client connected from ('127.0.0.1', 62555)
[LOAD BALANCER] Client connected from ('127.0.0.1', 62624)
[LOAD BALANCER] Client connected from ('127.0.0.1', 62627)
```


```bash
ASUS TUF GAMING A15@ASUSTUF-ALVINZP MINGW64 /d/KULIAH/FP PROGJAR/Runes-SteelFighter-Load Balancer
$ py server.py 8891
[SERVER] Running on port 8891...
[SERVER] Player 0 connected from ('127.0.0.1', 62625)
[SERVER] Player 1 connected from ('127.0.0.1', 62628)
```

```bash
ASUS TUF GAMING A15@ASUSTUF-ALVINZP MINGW64 /d/KULIAH/FP PROGJAR/Runes-SteelFighter-Load Balancer
$ py player.py 
pygame 2.6.1 (SDL 2.28.4, Python 3.11.9)
Hello from the pygame community. https://www.pygame.org/contribute.html
Connected as Player 0
```


```bash
ASUS TUF GAMING A15@ASUSTUF-ALVINZP MINGW64 /d/KULIAH/FP PROGJAR/Runes-SteelFighter-Load Balancer
$ py player.py 
pygame 2.6.1 (SDL 2.28.4, Python 3.11.9)
Hello from the pygame community. https://www.pygame.org/contribute.html
Connected as Player 1
```



```bash
ASUS TUF GAMING A15@ASUSTUF-ALVINZP MINGW64 /d/KULIAH/FP PROGJAR/Runes-SteelFighter-Load Balancer
$ py player.py 
pygame 2.6.1 (SDL 2.28.4, Python 3.11.9)
Hello from the pygame community. https://www.pygame.org/contribute.html
Connected as Player 0
```


```bash
ASUS TUF GAMING A15@ASUSTUF-ALVINZP MINGW64 /d/KULIAH/FP PROGJAR/Runes-SteelFighter-Load Balancer
$ py player.py 
pygame 2.6.1 (SDL 2.28.4, Python 3.11.9)
Hello from the pygame community. https://www.pygame.org/contribute.html
Connected as Player 1
```