# # AYZ - Yapay Zeka Asistanı

**A**vi | **Y**ırmızı | **Z**eşil renk temalı, Ollama ile yerel çalışan yapay zeka asistanı.

İki versiyon içerir:
- `ayz_cli.py` — terminal üzerinden çalışan sohbet asistanı
- `ayz_web.py` — Flask tabanlı web arayüzü

Model bulutta değil, **kendi bilgisayarında** [Ollama](https://ollama.com) üzerinden çalışır. Hiçbir API anahtarı gerekmez, veriler makinenden dışarı çıkmaz.

## Kurulum

1. [Ollama'yı indir ve kur](https://ollama.com/download)
2. Bir model indir:
   ```bash
   ollama pull llama3.1
   ```
3. Bağımlılıkları kur:
   ```bash
   pip install -r requirements.txt
   ```

## Kullanım

**Terminal versiyonu:**
```bash
python ayz_cli.py
```

**Web versiyonu:**
```bash
python ayz_web.py
```
Sonra tarayıcıda `http://localhost:5000` adresine git.

## Komutlar (CLI)

| Komut | Açıklama |
|---|---|
| `!help` | Komut listesi |
| `!status` | Ollama bağlantı durumu, model, hafıza |
| `!model <isim>` | Kullanılan modeli değiştir |
| `!clear` | Sohbet geçmişini temizle |
| `!save` | Hafızayı diske kaydet |
| `!exit` | Çıkış |
| `json:dosya.json` | Bir JSON dosyasını oku ve göster |

## Yapılandırma

`ayz_config.json` içinde:

```json
{
  "ollama_host": "http://localhost:11434",
  "ollama_model": "llama3.1",
  "voice": "Yelda",
  "language": "tr",
  "theme": "dark",
  "system_prompt": "Sen AYZ adında yardımsever bir yapay zeka asistanısın..."
}
```

- `ollama_model`: Hangi Ollama modelinin kullanılacağı (`ollama pull` ile indirilmiş olmalı)
- `system_prompt`: Asistanın karakterini/üslubunu belirleyen sistem talimatı — rol yapma senaryoları için burayı özelleştirebilirsin

## Model Önerileri (donanıma göre)

| Donanım | Önerilen model |
|---|---|
| ~8GB RAM | `mistral`, `llama3.2:3b` |
| ~16GB RAM | `llama3.1`, `qwen2.5:14b` |
| 24GB+ VRAM | `mistral-nemo` veya daha büyük modeller |

## Notlar

- Ses özelliği (`say` komutu) sadece **macOS**'ta çalışır.
- `ayz_memory.json` sohbet geçmişini tutar, bu repoya dahil edilmemiştir (bkz. `.gitignore`).
### 
