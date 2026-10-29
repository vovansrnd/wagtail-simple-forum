# wagtail-simple-forum

**Wagtail ile entegre bir tartışma forumu ekler: kategoriler, bölümler, konular, gönderiler, moderasyon, özel mesajlar, bildirimler, arama ve eski forum uygulamasından içe aktarma araçları.**

[English](README.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Nederlands](README.nl.md) · [Polski](README.pl.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## Temel özellikler

- Kategori → bölüm → konu → gönderi hiyerarşisi ve etkinlik sayaçları.
- Özel mesaj gelen kutusu ve dizili konuşmalar.
- Misafir anti-spam, moderasyon, arama ve hız sınırlaması.
- Eski forum için içe aktarma ve yönlendirme araçları; trafiği taşımadan önce dry-run sonucunu doğrulayın.

## Gereksinimler ve uyumluluk

- Bildirilen bağımlılıklar: `Wagtail >= 6.0; django-prose-editor >= 0.26; nh3 >= 0.2.14`.
- Python, Django ve Wagtail uyumluluğu birlikte kontrol edilmelidir. Paketin asgari bağımlılığı tüm sürümlerin desteklendiğini kanıtlamaz.

Paket metaverisi Wagtail >= 6.0 belirtir; ancak asgari bağımlılık, tüm sürümlerle uyumluluğu kanıtlamaz. Bu arşiv tüm Django/Wagtail kombinasyonları için tam otomatik test matrisi içermez. Üretimi yükseltmeden önce tam sürümleri, veritabanını, depolama arka ucunu ve dağıtım ayarlarını staging ortamında sınayın.

## Kurulum

Paketi Wagtail projenizle aynı sanal ortama yükleyin:

```bash
pip install wagtail-simple-forum
```

Diğer proje bağımlılıklarını koruyarak uygulamaları bu sırayla ekleyin:

```python
INSTALLED_APPS = [
    # Projenin zaten kullandığı diğer Django/Wagtail bağımlılıklarını da koruyun.
    "django_prose_editor",
    "wagtail_simple_forum",
]
```

Forum URL’lerini **Wagtail catch-all rotasından önce** ekleyin. Eski yönlendirmeler de bu rotadan önce olmalıdır.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls
urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,
    # Eski rotalar Wagtail catch-all rotasından önce gelmelidir.
]
```

`python manage.py migrate wagtail_simple_forum` çalıştırın.


## İlk yapılandırma

Başlangıç için en küçük örnek aşağıdadır. Model adlarını, API alanlarını ve URL’leri yapılandırmanıza uyarlayın.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls

urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,  # Eski rotalar Wagtail catch-all rotasından önce gelmelidir.
]
```

`python manage.py migrate wagtail_simple_forum` çalıştırın. Eski `forum` uygulaması için önce `python manage.py forum_import_from_app --source forum --dry-run` komutunu çalıştırın.

Eski forumu içe aktarmadan önce veritabanını yedekleyin ve `--dry-run` çalıştırın. İçe aktarma ve kontroller bitene kadar eski uygulamayı kurulu tutun.


## Önemli ayarlar ve davranış

Bu dizindeki İngilizce README, tüm seçenek tablolarını ve genişletilmiş örnekleri içeren temel başvuru belgesidir. Bu çeviri pratik kurulumu ve temel güvenlik uyarılarını kapsar; gelişmiş ayarları değiştirmeden önce İngilizce başvuruya bakın.

Tam ayar listesi için [İngilizce README](README.md) dosyasına bakın.

### Önemli notlar

Forum URL’leri ve eski yönlendirmeler Wagtail catch-all rotasından önce olmalıdır. Eski forumu içe aktarmadan önce yedek alın ve önce `--dry-run` çalıştırın.

## Güvenlik ve işletim

- Bağımlılıkları güncel tutun. Kullanıcı HTML’si için belirlenen temizleme/görüntüleme yolunu kullanın; kaydedilmiş yorumları veya forum gönderilerini koşulsuz `|safe` ile göstermeyin.
- Geçişleri ve izinleri normal, kısıtlı, moderatör ve yönetici hesaplarıyla kontrol edin.
- Çoklu site kurulumlarında yapılandırılmış her alan adını ve bilinmeyen bir hostu sınayın. Site bulunamazsa sorgu tüm sitelerdeki kayıtları kapsayacak şekilde genişlememelidir.
- API tokenlarını, SMTP kimlik bilgilerini ve özel URL’leri gizli kabul edin. Bunları Git’e eklemeyin veya herkese açık hata raporlarında paylaşmayın.
- Geçişler, toplu taşıma, içe aktarma veya ilk toplu yayın öncesinde veritabanını ve medya dosyalarını yedekleyin. Önce staging ortamında deneyin.

## Önerilen kombinasyonlar

- `wagtail-mptt-comments` foruma makale yorumlarını ekler; Prose seçicisi yalnızca özel alanlar için gerekir.
- Görsel dizinleri forum verilerinden bağımsızdır.

## Doğrulama kontrol listesi

- [ ] Aday sürümü staging ortamına kurun; Python, Django, Wagtail ve veritabanı sürümlerini kaydedin.
- [ ] `python manage.py check` ve paket geçişlerini çalıştırın.
- [ ] Ana akışı normal ve kısıtlı hesapla sınayın.
- [ ] Kayıtları, erişimi, önbelleği, yedeklemeyi ve geri yüklemeyi kontrol edin.

Arşiv statik sözdizimi ve paketleme kontrollerini geçer; ancak bu ortamda tam Django/Wagtail çalışma zamanı entegrasyonu test edilmedi. Aşağıdaki listeyi tüm sürümlerin test edildiğinin kanıtı değil, yayın öncesi zorunlu kontrol olarak görün.

## Sorun giderme

Akış çalışmıyorsa uygulama ayarlarını, geçişleri, URL sırasını, kullanıcı izinlerini ve Django kayıtlarını kontrol edin. Paket sürümünü ve örneği İngilizce README ile karşılaştırın.

## Lisans ve destek

MIT. Kaynak kod: [https://github.com/vovansrnd/wagtail-simple-forum](https://github.com/vovansrnd/wagtail-simple-forum).

