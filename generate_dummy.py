"""Generate 50 fictional CSV leads, reproducibly randomized. No real contacts."""
import csv
import random
from pathlib import Path


def main():
    rng = random.Random(20260920)
    names = ["Aditya", "Bella", "Citra", "Damar", "Eka", "Farah", "Galih", "Hana", "Intan", "Joko",
             "Kirana", "Laras", "Maya", "Nanda", "Oki", "Putri", "Raka", "Sari", "Tama", "Wulan"]
    surnames = ["Pratama", "Lestari", "Wijaya", "Saputra", "Permata", "Kusuma", "Utami", "Santoso"]
    sectors = ["Retail", "Logistik", "Studio", "Kuliner", "Properti", "Travel", "Edukasi", "Tekstil", "Digital", "Distribusi"]
    workflows = ["form website ke Google Sheets", "CRM ke notifikasi Telegram", "order toko ke laporan penjualan",
                 "email inquiry ke database lead", "invoice ke rekap administrasi"]
    templates = [
        ("AI automation", "Minggu depan", [5000000, 7500000, 10000000],
         'Kami ingin membeli jasa automation {workflow}. Budget sudah disetujui. Bisa jadwalkan diskusi? Target mulai minggu depan.'),
        ("API integration", "Minggu ini", [6000000, 12000000, 15000000],
         'We need to integrate {workflow}. We are ready to book a project discussion and start this week. Please send a proposal.'),
        ("Workflow automation", "Bulan ini", [2000000, 3000000, 4000000],
         'Kami tertarik menggunakan jasa integrasi {workflow}. Ingin diskusi ruang lingkup dulu, target implementasi bulan ini.'),
        ("Python automation", "Tiga bulan lagi", [500000, 1000000, 1500000],
         'Boleh minta penawaran untuk {workflow}? Dana kami terbatas. Rencana mulai tiga bulan lagi dan masih membandingkan vendor.'),
        ("AI automation", "Belum ada target", [None],
         'Sedang riset cara kerja {workflow}. Ada contoh studi kasus? Belum ada keputusan membeli, masih mengumpulkan informasi.'),
        ("LLM integration", "", [None, 0],
         'How does a local AI assistant work? We are exploring options for our internal team. No approved budget or launch date yet.'),
        ("Workflow automation", "Hari ini", [None],
         'Kami pelanggan lama. Workflow {workflow} error sejak pagi. Tolong bantu perbaiki koneksinya hari ini, bukan permintaan proyek baru.'),
        ("Desain logo", "Minggu depan", [2000000, 5000000],
         'Kami ingin memesan desain logo dan kemasan produk. Mulai minggu depan. Apakah menerima jasa desain grafis? Tidak butuh automation.'),
        ("", "", [None],
         'PROMO! Kami menjual paket backlink dan followers murah. Hubungi kami untuk membeli paket promosi, bukan mencari jasa Anda.'),
        ("", "", [None],
         'Halo, saya dapat kontak dari teman. Bisa kirim informasi layanan? Saya belum menjelaskan kebutuhan atau rencana pembelian.'),
    ]
    rows = []
    for index in range(50):
        service, timeline, budgets, template = templates[index % len(templates)]
        company = f"Dummy {rng.choice(sectors)} {index+1:02d}"
        row = dict(lead_id=f"DUMMY-{index+1:03d}", name=f"{rng.choice(names)} {rng.choice(surnames)}",
                   email=f"lead{index+1:03d}@example.com", company=company,
                   company_size=rng.choice([3, 8, 15, 25, 45, 80, 150, 250, None]),
                   budget=rng.choice(budgets), service=service, timeline=timeline,
                   message=template.format(workflow=rng.choice(workflows)) + f"\nPerusahaan: {company}.",
                   source=rng.choice(["website", "referral", "event", "email", "linkedin"]))
        rows.append(row)
    rng.shuffle(rows)
    target = Path(__file__).parent / "samples" / "dummy-leads-50.csv"
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Created {len(rows)} fictional leads: {target}")


if __name__ == "__main__":
    main()
