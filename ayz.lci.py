#!/usr/bin/env python3
"""
AYZ - Yapay Zeka Asistanı (Ollama / yerel model sürümü)
A = Mavi | Y = Kırmızı | Z = Yeşil
"""

import json
import datetime
import subprocess
import requests
from pathlib import Path

# ===== KONFIGÜRASYON =====
BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "ayz_config.json"
MEMORY_FILE = BASE_DIR / "ayz_memory.json"

DEFAULT_SYSTEM_PROMPT = (
    "Sen AYZ adında yardımsever bir yapay zeka asistanısın. "
    "Rol yapma senaryolarında karaktere sadık kal, akıcı ve doğal bir üslup kullan."
)


# ===== KONFIG OKU =====
def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception:
        config = {}
    config.setdefault("ollama_host", "http://localhost:11434")
    config.setdefault("ollama_model", "llama3.1")
    config.setdefault("voice", "Yelda")
    config.setdefault("language", "tr")
    config.setdefault("system_prompt", DEFAULT_SYSTEM_PROMPT)
    return config


def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ===== HAFIZA OKU =====
def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"identity": {}, "preferences": {}, "conversations": {}}


def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ===== OLLAMA BAĞLANTISI =====
def check_ollama_connection(host):
    """Ollama sunucusunun ayakta olup olmadığını kontrol eder"""
    try:
        r = requests.get(f"{host}/api/tags", timeout=3)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_ai_response(message, history=None):
    """Ollama'dan cevap al. history: [{'user':..., 'ai':...}, ...] (konuşma bağlamı için)"""
    config = load_config()
    host = config.get("ollama_host", "http://localhost:11434")
    model = config.get("ollama_model", "llama3.1")
    system_prompt = config.get("system_prompt", DEFAULT_SYSTEM_PROMPT)

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        for turn in history[-10:]:  # son 10 tur — bağlamı çok şişirmemek için
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["ai"]})
    messages.append({"role": "user", "content": message})

    try:
        response = requests.post(
            f"{host}/api/chat",
            json={"model": model, "messages": messages, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "").strip()
    except requests.exceptions.ConnectionError:
        return (
            f"⚠️ Ollama'ya bağlanılamadı ({host}). Terminalde 'ollama serve' "
            f"çalıştığından ve '{model}' modelinin indirildiğinden emin ol "
            f"(ollama pull {model})."
        )
    except requests.exceptions.Timeout:
        return "⚠️ Model yanıt vermekte gecikti (timeout). Daha küçük bir model deneyebilirsin."
    except Exception as e:
        return f"⚠️ Hata: {str(e)}"


# ===== SES ÇALMA (macOS) =====
def speak(text):
    """Metni sesli olarak okur"""
    try:
        subprocess.run(["say", "-v", "Yelda", text], check=False)
    except Exception:
        pass


# ===== ANA SINIF =====
class AYZ:
    def __init__(self):
        self.config = load_config()
        self.memory = load_memory()
        self.running = True
        self.history = []

    def chat(self, message):
        """Kullanıcı mesajını işle"""
        if not message.strip():
            return "Lütfen bir mesaj girin."

        if message.startswith("!"):
            return self.handle_command(message[1:].strip())

        if message.startswith("json:"):
            return self.handle_json(message[5:].strip())

        # AI cevabı al — geçmiş konuşmayı bağlam olarak gönderiyoruz
        response = get_ai_response(message, self.history)

        # Hafızaya kaydet
        self.history.append(
            {
                "user": message,
                "ai": response,
                "time": datetime.datetime.now().isoformat(),
            }
        )
        self.memory["conversations"][str(len(self.history))] = {
            "user": message,
            "ai": response,
        }
        save_memory(self.memory)

        # Sesli cevap
        speak(response[:100])  # İlk 100 karakter

        return response

    def handle_command(self, command):
        """! ile başlayan komutlar"""
        if command == "help":
            return """📖 AYZ Komutları:
!help      - Bu yardım menüsü
!status    - Sistem durumu
!model     - Kullanılan modeli göster/değiştir (örn: !model mistral)
!clear     - Sohbet geçmişini temizle
!exit      - Çıkış
!save      - Hafızayı kaydet
json:dosya - JSON dosyasını oku"""

        if command == "status":
            host = self.config.get("ollama_host", "http://localhost:11434")
            ollama_up = check_ollama_connection(host)
            return f"""📊 AYZ Durumu:
Ollama: {'✅ çalışıyor' if ollama_up else '❌ ulaşılamıyor'}
Model: {self.config.get('ollama_model', 'llama3.1')}
Ses: {'✅' if self.config.get('voice') else '❌'}
Hafıza: {len(self.memory.get('conversations', {}))} kayıt"""

        if command.startswith("model"):
            parts = command.split(maxsplit=1)
            if len(parts) == 1:
                return f"🧠 Şu anki model: {self.config.get('ollama_model', 'llama3.1')}"
            new_model = parts[1].strip()
            self.config["ollama_model"] = new_model
            save_config(self.config)
            return f"🧠 Model değiştirildi: {new_model} (indirilmediyse: ollama pull {new_model})"

        if command == "clear":
            self.history = []
            self.memory["conversations"] = {}
            save_memory(self.memory)
            return "🧹 Sohbet geçmişi temizlendi."

        if command == "save":
            save_memory(self.memory)
            return "💾 Hafıza kaydedildi."

        if command == "exit":
            self.running = False
            return "👋 Görüşürüz!"

        return f"❌ Bilinmeyen komut: {command}. !help yaz."

    def handle_json(self, path):
        """JSON dosyasını oku"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except FileNotFoundError:
            return f"❌ Dosya bulunamadı: {path}"
        except Exception as e:
            return f"❌ JSON okuma hatası: {str(e)}"

    def run(self):
        """Ana döngü"""
        print("╔════════════════════════════════════════════════╗")
        print("║   🧠  A Y Z  -  Yapay Zeka Asistanı          ║")
        print("║    A = Mavi    Y = Kırmızı   Z = Yeşil       ║")
        print("╚════════════════════════════════════════════════╝")
        print("")

        host = self.config.get("ollama_host", "http://localhost:11434")
        if not check_ollama_connection(host):
            print("⚠️  Ollama'ya ulaşılamıyor. Terminalde 'ollama serve' çalıştırdığından emin ol.")
            print(f"   Model indirmek için: ollama pull {self.config.get('ollama_model', 'llama3.1')}")
            print("")

        print("  💬 Mesaj yaz, !help ile komutları gör.")
        print("  🎤 Sesli yanıtlar için 'say' komutu kullanılıyor.")
        print("")

        while self.running:
            try:
                user_input = input("🧑 Siz: ").strip()
                if not user_input:
                    continue

                if user_input.lower() in ["exit", "çıkış"]:
                    print("👋 Görüşürüz!")
                    break

                response = self.chat(user_input)
                print(f"🤖 AYZ: {response}")
                print("")

            except KeyboardInterrupt:
                print("\n👋 Görüşürüz!")
                break
            except Exception as e:
                print(f"❌ Hata: {e}")


# ===== ÇALIŞTIR =====
if __name__ == "__main__":
    ayz = AYZ()
    ayz.run()
