import os
import random
import requests
import tweepy

# --- FUNGSI 1: MENDAPATKAN POSTINGAN ACAK DARI FILE TXT ---
def get_random_post(filename="post.txt"):
    """
    Membaca file post.txt, memisahkan postingan berdasarkan pemisah '---',
    dan memilih satu blok postingan utuh secara acak.

    Args:
        filename (str): Nama file yang berisi postingan. Defaultnya adalah "post.txt".

    Returns:
        str: Sebuah string postingan yang dipilih secara acak.
             Mengembalikan None jika file tidak ditemukan atau kosong.
    """
    try:
        # Membuka dan membaca keseluruhan isi file
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # Memecah konten menjadi daftar postingan menggunakan '---' sebagai pemisah.
        # `post.strip()` digunakan untuk membersihkan spasi atau baris kosong
        # di sekitar setiap postingan agar rapi.
        posts = [post.strip() for post in content.split('---') if post.strip()]

        # Memilih satu postingan secara acak dari daftar jika daftar tidak kosong
        return random.choice(posts) if posts else None

    except FileNotFoundError:
        print(f"Error: File '{filename}' tidak ditemukan. Pastikan file tersebut ada di direktori yang sama.")
        return None
    except Exception as e:
        print(f"Terjadi error saat membaca file '{filename}': {e}")
        return None

# --- FUNGSI 2: MENDAPATKAN LINK GAMBAR ACAK ---
def get_random_image_link(filename="image.txt"):
    """
    Membaca file image.txt dan memilih satu URL gambar secara acak.

    Args:
        filename (str): Nama file yang berisi URL gambar. Defaultnya adalah "image.txt".

    Returns:
        str: Sebuah string URL gambar yang dipilih secara acak.
             Mengembalikan None jika file tidak ditemukan atau kosong.
    """
    try:
        # Membuka file dan membaca semua baris
        with open(filename, 'r') as f:
            # Membuat daftar link dan membersihkan spasi/baris kosong
            links = [line.strip() for line in f if line.strip()]

        # Memilih satu link secara acak dari daftar jika daftar tidak kosong
        return random.choice(links) if links else None

    except FileNotFoundError:
        print(f"Error: File '{filename}' tidak ditemukan. Pastikan Anda sudah membuatnya.")
        return None

# --- FUNGSI 3: MEMPOSTING KONTEN KE X.COM ---
def post_to_x(text_to_post, image_url=None):
    """
    Memposting teks dan (opsional) gambar ke akun X.com menggunakan API.

    Args:
        text_to_post (str): Teks yang akan dijadikan tweet.
        image_url (str, optional): URL gambar yang akan diunggah dan dilampirkan.
    """
    try:
        # Mengunggah media (gambar) memerlukan otentikasi API v1.1
        auth = tweepy.OAuth1UserHandler(
            os.getenv('X_API_KEY'), os.getenv('X_API_SECRET'),
            os.getenv('X_ACCESS_TOKEN'), os.getenv('X_ACCESS_TOKEN_SECRET')
        )
        api_v1 = tweepy.API(auth)

        # Memposting tweet (teks + media_id) menggunakan API v2
        client_v2 = tweepy.Client(
            bearer_token=os.getenv('X_BEARER_TOKEN'),
            consumer_key=os.getenv('X_API_KEY'),
            consumer_secret=os.getenv('X_API_SECRET'),
            access_token=os.getenv('X_ACCESS_TOKEN'),
            access_token_secret=os.getenv('X_ACCESS_TOKEN_SECRET')
        )

        media_id = None
        # Proses hanya jika ada URL gambar yang diberikan
        if image_url:
            print(f"Mengunduh gambar dari: {image_url}")
            filename = 'temp_image_for_post.jpg' # Nama file sementara
            response = requests.get(image_url, stream=True)

            if response.status_code == 200:
                # Menyimpan gambar yang diunduh ke file sementara
                with open(filename, 'wb') as image_file:
                    for chunk in response.iter_content(1024):
                        image_file.write(chunk)

                # Mengunggah media ke X.com menggunakan API v1.1 untuk mendapatkan media_id
                print("Mengunggah gambar ke X.com...")
                media = api_v1.media_upload(filename=filename)
                media_id = media.media_id_string
                print(f"Gambar berhasil di-upload. Media ID: {media_id}")

                # Menghapus file gambar sementara setelah berhasil diunggah
                os.remove(filename)
            else:
                print(f"Gagal mengunduh gambar. Status code: {response.status_code}")

        # Membuat tweet menggunakan API v2
        print("Membuat tweet...")
        if media_id:
            # Jika ada media_id, lampirkan ke tweet
            response = client_v2.create_tweet(text=text_to_post, media_ids=[media_id])
        else:
            # Jika tidak ada media, post hanya teks
            response = client_v2.create_tweet(text=text_to_post)

        print(f"🎉 Berhasil memposting tweet! ID Tweet: {response.data['id']}")

    except Exception as e:
        print(f"❌ Error saat memposting ke X.com: {e}")

# --- FUNGSI UTAMA (MAIN EXECUTION BLOCK) ---
if __name__ == "__main__":
    """
    Blok ini akan dieksekusi saat skrip dijalankan secara langsung.
    """
    print("=============================================")
    print("Memulai proses auto-posting ke X.com...")
    print("=============================================")

    # 1. Mendapatkan teks postingan acak dari post.txt
    post_text = get_random_post()

    # Lanjutkan hanya jika postingan berhasil didapatkan
    if post_text:
        print("\n--- KONTEN DIPILIH ---")
        print("Teks Postingan:")
        print(post_text)
        print("----------------------\n")

        # 2. Mengambil link gambar acak dari image.txt
        image_url = get_random_image_link()
        if image_url:
            print(f"URL Gambar yang dipilih: {image_url}\n")
        else:
            print("Tidak ada URL gambar yang ditemukan, akan memposting tanpa gambar.\n")

        # 3. Posting ke X.com dengan teks dan gambar (jika ada)
        post_to_x(post_text, image_url)
    else:
        print("Tidak ada postingan yang bisa dipilih dari post.txt. Proses dihentikan.")

    print("\n=============================================")
    print("Proses selesai.")
    print("=============================================")