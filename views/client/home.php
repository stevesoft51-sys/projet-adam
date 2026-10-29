<?php
$pageTitle = 'Accueil';

$featuredFallbacks = [
    'https://images.pexels.com/photos/3763847/pexels-photo-3763847.jpeg?auto=compress&cs=tinysrgb&w=800',
    'https://images.pexels.com/photos/1279330/pexels-photo-1279330.jpeg?auto=compress&cs=tinysrgb&w=800',
    'https://images.pexels.com/photos/769289/pexels-photo-769289.jpeg?auto=compress&cs=tinysrgb&w=800',
    'https://images.pexels.com/photos/4253315/pexels-photo-4253315.jpeg?auto=compress&cs=tinysrgb&w=800',
];

$placeholderPool = [
    'https://images.pexels.com/photos/2374946/pexels-photo-2374946.jpeg?auto=compress&cs=tinysrgb&w=800',
    'https://images.pexels.com/photos/5779364/pexels-photo-5779364.jpeg?auto=compress&cs=tinysrgb&w=800',
    'https://images.pexels.com/photos/9510363/pexels-photo-9510363.jpeg?auto=compress&cs=tinysrgb&w=800',
    'https://images.pexels.com/photos/6747870/pexels-photo-6747870.jpeg?auto=compress&cs=tinysrgb&w=800',
    'https://images.pexels.com/photos/316909/pexels-photo-316909.jpeg?auto=compress&cs=tinysrgb&w=800',
    'https://images.pexels.com/photos/4467605/pexels-photo-4467605.jpeg?auto=compress&cs=tinysrgb&w=800',
];

$menuItems = [];
foreach ($products ?? [] as $i => $p) {
    $menuItems[] = [
        'cat' => $p['category_name'],
        'name' => $p['name'],
        'desc' => (string)($p['description'] ?? ''),
        'price' => number_format((float)$p['price'], 0, ',', ' ') . ' FCFA',
        'image' => !empty($p['image']) ? $p['image'] : $placeholderPool[$i % count($placeholderPool)],
    ];
}
$menuJson = json_encode($menuItems, JSON_UNESCAPED_UNICODE | JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT);
$reservationErrors = $_SESSION['errors'] ?? [];
unset($_SESSION['errors'], $_SESSION['old']);
?>
<!doctype html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="csrf-token" content="<?= htmlspecialchars($_SESSION['csrf_token'] ?? '') ?>">
  <title>Restaurant Adam - Ngaoundéré</title>
  <script src="https://cdn.tailwindcss.com/3.4.17"></script>
  <script src="https://cdn.jsdelivr.net/npm/lucide@0.263.0/dist/umd/lucide.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&amp;family=Work+Sans:wght@300;400;500;600&amp;display=swap" rel="stylesheet">
  <style>
        :root { --gold: #c9a96e; --dark: #1a1a1a; --cream: #faf6f0; }
        body { font-family: 'Work Sans', sans-serif; }
        .font-display { font-family: 'Playfair Display', serif; }
        .scroll-smooth { scroll-behavior: smooth; }
        .hero-overlay { background: linear-gradient(135deg, rgba(26,26,26,0.75) 0%, rgba(26,26,26,0.3) 100%); }
        .gold-underline { position: relative; display: inline-block; }
        .gold-underline::after { content:''; position:absolute; bottom:-4px; left:0; width:60%; height:2px; background:var(--gold); }
        .btn-gold { background: var(--gold); color: #1a1a1a; font-weight: 600; transition: all .2s; }
        .btn-gold:hover { background: #b8944f; transform: translateY(-1px); }
        .btn-outline { border: 2px solid var(--gold); color: var(--gold); font-weight: 500; transition: all .2s; }
        .btn-outline:hover { background: var(--gold); color: #1a1a1a; }
        .card-dish { transition: transform .2s; }
        .card-dish:hover { transform: translateY(-4px); }
        #catalog-grid button img { display:block; aspect-ratio: 16 / 10; object-fit: cover; }
        .field-error { color: #f87171; font-size: 12px; margin-top: 4px; display: none; }
        .field-error.visible { display: block; }
    </style>
</head>
<body class="scroll-smooth w-full" style="background: rgb(26, 26, 26);">
  <!-- Header -->
  <header class="fixed top-0 left-0 right-0 z-50 bg-[#1a1a1a]/95 backdrop-blur-sm border-b border-white/10">
   <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
    <a href="/" class="font-display text-xl text-[#c9a96e]" style="color: rgb(201, 169, 110); font-weight: 700;">Restaurant Adam</a>
    <nav class="hidden md:flex items-center gap-6 text-sm text-white/80">
     <a href="#menu" class="hover:text-[#c9a96e] transition">Le Menu</a>
     <a href="#avantages" class="hover:text-[#c9a96e] transition">Notre Histoire</a>
     <a href="#reservation" class="hover:text-[#c9a96e] transition">Réserver</a>
    </nav>
    <div class="flex items-center gap-4">
     <a href="tel:+237694469678" class="hidden sm:flex items-center gap-1 text-white/80 text-sm hover:text-[#c9a96e]"> <i data-lucide="phone" style="width:14px;height:14px"></i> <span>+237 694 469 678</span> </a>
     <a href="#reservation" class="btn-gold px-4 py-2 rounded-md text-sm">Réserver une table</a>
    </div>
   </div>
  </header>

  <!-- Hero -->
  <section class="relative w-full" style="height: 90vh;">
   <img class="absolute inset-0 w-full h-full object-cover" loading="lazy" src="https://images.pexels.com/photos/262978/pexels-photo-262978.jpeg?auto=compress&amp;cs=tinysrgb&amp;w=1280" alt="Service élégant dans un restaurant chaleureux">
   <div class="hero-overlay absolute inset-0"></div>
   <div class="relative z-10 flex flex-col items-center justify-center h-full text-center px-4">
    <p class="text-[#c9a96e] uppercase tracking-[0.2em] text-sm mb-4">Restaurant Adam · Ngaoundéré, au bois de Mardock</p>
    <h1 class="font-display text-white text-4xl md:text-6xl font-bold mb-4 max-w-3xl leading-tight">Restaurant Adam, l'expérience gourmande de Ngaoundéré</h1>
    <p class="text-white/80 text-lg md:text-xl mb-6 max-w-xl">Produits frais, recettes créatives et service attentionné au bois de Mardock, à Ngaoundéré.</p>
    <div class="flex items-center gap-2 mb-8">
     <span class="text-[#c9a96e] text-lg">★★★★★</span> <span class="text-white/70 text-sm">4.9/5 - Plus de 320 avis vérifiés</span>
    </div>
    <div class="flex flex-col sm:flex-row gap-4">
     <a href="#reservation" class="btn-gold px-8 py-3 rounded-md text-base">Réserver maintenant</a>
     <a href="#menu" class="btn-outline px-8 py-3 rounded-md text-base">Voir le menu</a>
    </div>
   </div>
  </section>

  <!-- Trust -->
  <section class="py-12 border-b border-white/10" style="background: rgb(21, 21, 21);">
   <div class="max-w-5xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
    <div>
     <p class="font-display text-3xl text-[#c9a96e]">12</p>
     <p class="text-sm text-white/60 mt-1">Années d'expérience</p>
    </div>
    <div>
     <p class="font-display text-3xl text-[#c9a96e]">320+</p>
     <p class="text-sm text-white/60 mt-1">Avis 5 étoiles</p>
    </div>
    <div>
     <p class="font-display text-3xl text-[#c9a96e]">100%</p>
     <p class="text-sm text-white/60 mt-1">Produits frais &amp; locaux</p>
    </div>
    <div>
     <p class="font-display text-3xl text-[#c9a96e]">45</p>
     <p class="text-sm text-white/60 mt-1">Couverts en terrasse</p>
    </div>
   </div>
  </section>

  <!-- Plats Signatures -->
  <section id="menu" class="py-20 px-4">
   <div class="max-w-6xl mx-auto">
    <p class="text-center text-[#c9a96e] uppercase tracking-widest text-sm mb-2">Nos créations</p>
    <h2 class="font-display text-center text-white text-3xl md:text-4xl font-bold mb-6">Les Incontournables</h2>
    <div class="text-center mb-12"><a href="#full-menu" id="full-menu-link" class="btn-gold inline-flex items-center gap-2 px-6 py-3 rounded-md text-base shadow-lg">Voir tout le menu <i data-lucide="arrow-right" style="width:18px;height:18px"></i></a>
    </div>
    <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
<?php if (!empty($featured)): foreach (array_slice($featured, 0, 4) as $i => $dish): ?>
     <div class="card-dish rounded-xl overflow-hidden" style="background: rgb(37, 37, 37);">
      <img class="w-full h-48 object-cover" loading="lazy" src="<?= View::e($dish['image'] ?: $featuredFallbacks[$i % count($featuredFallbacks)]) ?>" alt="<?= View::e($dish['name']) ?>">
      <div class="p-4">
       <h3 class="font-display text-white font-semibold mb-1"><?= View::e($dish['name']) ?></h3>
       <p class="text-white/60 text-sm mb-3"><?= View::e(mb_strimwidth((string)($dish['description'] ?? ''), 0, 90, '…')) ?></p>
       <div class="flex items-center justify-between">
        <span class="text-[#c9a96e] font-semibold"><?= View::money((float)$dish['price']) ?></span>
        <a href="#reservation" class="text-xs btn-outline px-3 py-1 rounded">Réserver</a>
       </div>
      </div>
     </div>
<?php endforeach; else: ?>
     <p class="col-span-full text-center text-white/50 py-10">La carte sera bientôt disponible.</p>
<?php endif; ?>
    </div>
   </div>
  </section>

  <!-- Avantages -->
  <section id="avantages" class="py-20 px-4" style="background: rgb(21, 21, 21);">
   <div class="max-w-5xl mx-auto">
    <h2 class="font-display text-center text-white text-3xl font-bold mb-12">Pourquoi Nos Clients Reviennent</h2>
    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
     <div class="text-center">
      <div class="w-12 h-12 mx-auto mb-3 rounded-full bg-[#c9a96e]/20 flex items-center justify-center"><i data-lucide="leaf" style="width:22px;height:22px;color:#c9a96e"></i></div>
      <h3 class="text-white font-semibold mb-1">Produits Ultra-Frais</h3>
      <p class="text-white/60 text-sm">Approvisionnement quotidien auprès de producteurs locaux sélectionnés.</p>
     </div>
     <div class="text-center">
      <div class="w-12 h-12 mx-auto mb-3 rounded-full bg-[#c9a96e]/20 flex items-center justify-center"><i data-lucide="clock" style="width:22px;height:22px;color:#c9a96e"></i></div>
      <h3 class="text-white font-semibold mb-1">Service Rapide &amp; Attentif</h3>
      <p class="text-white/60 text-sm">Plats servis en 15 minutes, votre pause déjeuner est préservée.</p>
     </div>
     <div class="text-center">
      <div class="w-12 h-12 mx-auto mb-3 rounded-full bg-[#c9a96e]/20 flex items-center justify-center"><i data-lucide="heart" style="width:22px;height:22px;color:#c9a96e"></i></div>
      <h3 class="text-white font-semibold mb-1">Ambiance Intimiste</h3>
      <p class="text-white/60 text-sm">Un cadre chaleureux et élégant pour vos moments en duo ou entre amis.</p>
     </div>
    </div>
   </div>
  </section>

  <!-- Ambiance -->
  <section class="py-20 px-4">
   <div class="max-w-6xl mx-auto grid md:grid-cols-2 gap-10 items-center">
    <div>
     <img class="w-full h-80 object-cover rounded-xl" loading="lazy" src="https://images.pexels.com/photos/262047/pexels-photo-262047.jpeg?auto=compress&amp;cs=tinysrgb&amp;w=1280" alt="Intérieur luxueux d'un restaurant avec lustres et fauteuils élégants">
    </div>
    <div>
     <p class="text-[#c9a96e] uppercase tracking-widest text-sm mb-2">L'expérience</p>
     <h2 class="font-display text-white text-3xl font-bold mb-4">Un Voyage pour les Sens</h2>
     <p class="text-white/70 leading-relaxed mb-6">Chaque détail a été pensé pour éveiller vos sens : lumières tamisées, musique douce, vaisselle artisanale et saveurs qui racontent une histoire. Offrez-vous une parenthèse gourmande inoubliable.</p>
     <a href="#reservation" class="btn-gold px-6 py-3 rounded-md inline-block">Réserver votre soirée</a>
    </div>
   </div>
  </section>

  <!-- Reservation -->
  <section id="reservation" class="py-20 px-4" style="background: rgb(17, 17, 17);">
   <div class="max-w-4xl mx-auto">
    <h2 class="font-display text-center text-white text-3xl font-bold mb-3">Réservez Votre Table</h2>
    <p class="text-center text-white/60 mb-10">Réservez votre table à Ngaoundéré · Contact : <?= View::e($settings['restaurant_phone'] ?? '+237 694 469 678') ?></p>
    <div class="grid md:grid-cols-2 gap-10">
     <form id="reservation-form" method="post" action="/reservation" class="space-y-4">
      <?= csrf_field() ?>
      <div>
       <label for="customer_name" class="text-white/80 text-sm block mb-1">Nom complet</label>
       <input id="customer_name" name="customer_name" type="text" required class="w-full bg-white/10 border border-white/20 rounded-md px-4 py-2.5 text-white placeholder-white/40 focus:border-[#c9a96e] focus:outline-none">
       <p class="field-error" data-error-for="customer_name"></p>
      </div>
      <div class="grid grid-cols-2 gap-4">
       <div>
        <label for="customer_email" class="text-white/80 text-sm block mb-1">Email</label>
        <input id="customer_email" name="customer_email" type="email" class="w-full bg-white/10 border border-white/20 rounded-md px-4 py-2.5 text-white placeholder-white/40 focus:border-[#c9a96e] focus:outline-none">
        <p class="field-error" data-error-for="customer_email"></p>
       </div>
       <div>
        <label for="customer_phone" class="text-white/80 text-sm block mb-1">Téléphone</label>
        <input id="customer_phone" name="customer_phone" type="tel" required class="w-full bg-white/10 border border-white/20 rounded-md px-4 py-2.5 text-white placeholder-white/40 focus:border-[#c9a96e] focus:outline-none">
        <p class="field-error" data-error-for="customer_phone"></p>
       </div>
      </div>
      <div class="grid grid-cols-3 gap-4">
       <div>
        <label for="date" class="text-white/80 text-sm block mb-1">Date</label>
        <input id="date" name="date" type="date" required min="<?= date('Y-m-d') ?>" class="w-full bg-white/10 border border-white/20 rounded-md px-4 py-2.5 text-white focus:border-[#c9a96e] focus:outline-none">
        <p class="field-error" data-error-for="date"></p>
       </div>
       <div>
        <label for="time" class="text-white/80 text-sm block mb-1">Heure</label>
        <input id="time" name="time" type="time" required class="w-full bg-white/10 border border-white/20 rounded-md px-4 py-2.5 text-white focus:border-[#c9a96e] focus:outline-none">
        <p class="field-error" data-error-for="time"></p>
       </div>
       <div>
        <label for="guests" class="text-white/80 text-sm block mb-1">Convives</label>
        <input id="guests" name="guests" type="number" min="1" max="20" value="2" required class="w-full bg-white/10 border border-white/20 rounded-md px-4 py-2.5 text-white focus:border-[#c9a96e] focus:outline-none">
        <p class="field-error" data-error-for="guests"></p>
       </div>
      </div>
      <div>
       <label for="notes" class="text-white/80 text-sm block mb-1">Message (optionnel)</label>
       <textarea id="notes" name="notes" rows="2" class="w-full bg-white/10 border border-white/20 rounded-md px-4 py-2.5 text-white placeholder-white/40 focus:border-[#c9a96e] focus:outline-none resize-none"></textarea>
       <p class="field-error" data-error-for="notes"></p>
      </div>
      <button type="submit" class="btn-gold w-full py-3 rounded-md text-base">Confirmer ma réservation</button>
      <div id="form-errors" class="hidden rounded-md bg-red-500/10 border border-red-400/30 px-4 py-3 text-red-300 text-sm"></div>
      <p class="text-center text-white/40 text-xs mt-2">Réponse sous 30 min · Vos données restent confidentielles</p>
      <!-- Success message -->
      <div id="form-success" class="hidden text-center py-4">
       <p class="text-[#c9a96e] font-semibold">✓ Réservation envoyée ! Votre code : <span id="success-code" class="font-bold"></span></p>
       <a id="success-ticket-link" href="#" class="inline-block mt-3 btn-gold px-6 py-2 rounded-md text-sm">Voir mon ticket</a>
      </div>
     </form>
     <div class="space-y-6">
      <div>
       <h3 class="text-white font-semibold mb-2">Horaires</h3>
       <p class="text-white/60 text-sm whitespace-pre-line">Lun – Ven : <?= View::e($settings['opening_time'] ?? '12h00') ?> – 14h30 / 19h – <?= View::e($settings['closing_time'] ?? '22h30') . "\n" ?>Sam – Dim : 12h – 15h / 19h – 23h</p>
      </div>
      <div>
       <h3 class="text-white font-semibold mb-2">Adresse</h3>
       <p class="text-white/60 text-sm"><?= View::e($settings['restaurant_address'] ?? 'Ngaoundéré, au bois de Mardock') ?></p>
      </div>
      <a href="tel:+237694469678" class="flex items-center gap-2 text-[#c9a96e] hover:underline"> <i data-lucide="phone" style="width:16px;height:16px"></i> <span>Appelez-nous : +237 694 469 678</span> </a>
     </div>
    </div>
   </div>
  </section>

  <!-- Menu complet, affiché comme une seconde page interne -->
  <section id="full-menu" class="hidden min-h-screen bg-[#faf6f0] text-[#1a1a1a] py-24 px-4">
   <div class="max-w-6xl mx-auto">
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8">
     <div>
      <a href="#menu" class="inline-flex items-center gap-2 text-[#8b6b38] text-sm mb-4"><i data-lucide="arrow-left" style="width:16px;height:16px"></i> Retour à l'accueil</a>
      <p class="text-[#b08b50] uppercase tracking-[0.2em] text-xs">Restaurant Adam · Ngaoundéré</p>
      <h2 class="font-display text-4xl md:text-5xl font-bold mt-2">Le menu complet</h2>
      <p class="text-black/60 mt-3 max-w-xl">Des recettes généreuses, préparées avec soin. Cliquez sur un plat pour découvrir ses détails.</p>
     </div>
     <div class="w-full md:w-72">
      <label for="menu-search" class="sr-only">Rechercher dans le menu</label>
      <div class="relative"><i data-lucide="search" class="absolute left-3 top-1/2 -translate-y-1/2 text-black/40" style="width:18px;height:18px"></i><input id="menu-search" type="search" placeholder="Rechercher un plat..." class="w-full rounded-md border border-black/10 bg-white py-3 pl-10 pr-4 outline-none focus:border-[#c9a96e]"></div>
     </div>
    </div>
    <div id="menu-filters" class="flex gap-2 overflow-x-auto pb-3 mb-8"></div>
    <div id="catalog-grid" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5"></div>
    <p id="menu-empty" class="hidden text-center py-16 text-black/50">Aucun élément ne correspond à votre recherche.</p>
   </div>
  </section>

  <div id="dish-modal" class="hidden fixed inset-0 z-[60] bg-black/70 p-4 items-center justify-center" role="dialog" aria-modal="true" aria-labelledby="modal-dish-name">
   <div class="w-full max-w-md rounded-2xl bg-[#faf6f0] p-7 shadow-2xl">
    <div class="flex justify-between items-start gap-4">
     <div>
      <p id="modal-category" class="text-[#b08b50] uppercase tracking-widest text-xs"></p>
      <h2 id="modal-dish-name" class="font-display text-3xl font-bold mt-2"></h2>
     </div>
     <button id="modal-close" type="button" aria-label="Fermer" class="rounded-full p-2 hover:bg-black/10"><i data-lucide="x" style="width:20px;height:20px"></i></button>
    </div>
    <img id="modal-image" src="" alt="" class="hidden w-full h-44 object-cover rounded-lg mt-4">
    <p id="modal-desc" class="text-black/60 mt-4"></p>
    <p id="modal-price" class="text-[#9a7438] font-semibold text-xl mt-5"></p>
    <div class="mt-5 border-t border-black/10 pt-5">
     <p class="text-black/60">Une création Restaurant Adam, servie dans une ambiance chaleureuse et premium.</p>
     <p class="mt-4 text-[#9a7438] font-semibold">★ <span id="modal-rating">4.9/5</span></p>
    </div>
    <a href="#reservation" id="modal-reserve" class="btn-gold mt-6 block text-center py-3 rounded-md">Réserver une table</a>
   </div>
  </div>

  <!-- Footer -->
  <footer class="border-t border-white/10 py-10 px-4" style="background: rgb(17, 17, 17);">
   <div class="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
    <p class="text-white/40 text-sm">© <?= date('Y') ?> Restaurant Adam · Ngaoundéré, au bois de Mardock</p>
    <div class="flex items-center gap-4">
     <a href="/login" class="text-white/40 text-sm hover:text-[#c9a96e] transition">Espace personnel</a>
     <a href="#reservation" class="btn-outline px-5 py-2 rounded-md text-sm">Réserver une table</a>
    </div>
   </div>
  </footer>

  <script>
    const menuItems = <?= $menuJson ?>;
    const catalog = document.getElementById('catalog-grid'), filters = document.getElementById('menu-filters'), search = document.getElementById('menu-search');
    const categories = ['TOUS', ...new Set(menuItems.map(item => item.cat))]; let activeCategory = 'TOUS';

    function renderFilters(){
      filters.innerHTML = categories.map(c => `<button type="button" data-category="${encodeURIComponent(c)}" class="rounded-full border px-4 py-2 text-sm whitespace-nowrap ${c===activeCategory?'bg-[#1a1a1a] text-white':'border-black/15 hover:border-[#c9a96e]'}">${c}</button>`).join('');
      filters.querySelectorAll('button').forEach(b=>b.onclick=()=>{activeCategory=b.dataset.category;renderFilters();renderMenu()});
    }

    function renderMenu(){
      const term=search.value.toLowerCase();
      const shown=menuItems.map((item,idx)=>({item,idx})).filter(({item})=>(activeCategory==='TOUS'||item.cat===activeCategory)&&item.name.toLowerCase().includes(term));
      catalog.innerHTML=shown.map(({item})=>{
        return `<button type="button" class="text-left rounded-xl bg-white border border-black/5 overflow-hidden shadow-sm transition hover:-translate-y-1 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-[#c9a96e]" data-name="${encodeURIComponent(item.name)}"><img src="${item.image}" alt="${item.name.replace(/"/g,'&quot;')}" loading="lazy" class="w-full h-44 object-cover"><div class="p-5"><span class="text-[#b08b50] text-xs uppercase tracking-widest">${item.cat}</span><span class="block font-display text-xl font-semibold mt-3">${item.name}</span><span class="block text-[#9a7438] font-semibold mt-4">${item.price}</span></div></button>`
      }).join('');
      document.getElementById('menu-empty').classList.toggle('hidden',shown.length>0);
      catalog.querySelectorAll('[data-name]').forEach(card=>card.onclick=()=>openDish(menuItems.find(m=>m.name===decodeURIComponent(card.dataset.name))));
    }

    function openDish(item){
      document.getElementById('modal-category').textContent=item.cat;
      document.getElementById('modal-dish-name').textContent=item.name;
      document.getElementById('modal-price').textContent=item.price;
      const desc=document.getElementById('modal-desc');
      desc.textContent=item.desc||'Une création Restaurant Adam, préparée avec des produits frais du jour.';
      const img=document.getElementById('modal-image');
      img.src=item.image; img.alt=item.name; img.classList.remove('hidden');
      document.getElementById('dish-modal').classList.remove('hidden');
      document.getElementById('dish-modal').classList.add('flex');
    }

    function closeDish(){document.getElementById('dish-modal').classList.add('hidden');document.getElementById('dish-modal').classList.remove('flex');}

    renderFilters();renderMenu();
    search.addEventListener('input',renderMenu);
    document.getElementById('modal-close').onclick=closeDish;
    document.getElementById('dish-modal').onclick=e=>{if(e.target.id==='dish-modal')closeDish()};
    document.getElementById('modal-reserve').onclick=closeDish;

    const homeSections = document.querySelectorAll('body > header, body > section:not(#full-menu), body > footer');
    function showPage(){const menu=location.hash==='#full-menu';homeSections.forEach(el=>el.classList.toggle('hidden',menu));document.getElementById('full-menu').classList.toggle('hidden',!menu);if(menu)window.scrollTo(0,0)}
    window.addEventListener('hashchange',showPage);showPage();

    // ---- Reservation form (backend /reservation) ----
    const form = document.getElementById('reservation-form');
    const successEl = document.getElementById('form-success');
    const errorsEl = document.getElementById('form-errors');
    const submitBtn = form.querySelector('[type="submit"]');

    function clearErrors(){
      errorsEl.classList.add('hidden'); errorsEl.textContent='';
      document.querySelectorAll('.field-error').forEach(el=>{el.classList.remove('visible');el.textContent='';});
    }

    function showErrors(errors){
      let first = '';
      Object.entries(errors).forEach(([field,messages])=>{
        const el = document.querySelector(`[data-error-for="${field}"]`);
        if(el){el.textContent=Array.isArray(messages)?messages[0]:messages;el.classList.add('visible');if(!first)first=el.textContent;}
      });
      if(!Object.keys(errors).length){errorsEl.textContent='Une erreur est survenue. Veuillez réessayer.';}
      else if(!document.querySelector('.field-error.visible') && first===null){}
      if(!document.querySelector('.field-error.visible')){
        errorsEl.textContent='Veuillez corriger les erreurs puis réessayer.';
      }
      errorsEl.classList.remove('hidden');
    }

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearErrors();
      submitBtn.disabled = true;
      submitBtn.style.opacity = '0.5';
      submitBtn.textContent = 'Envoi en cours…';

      try {
        const res = await fetch('/reservation', {
          method: 'POST',
          body: new FormData(form),
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await res.json().catch(() => ({}));

        if (res.ok && data.ok) {
          form.reset();
          document.getElementById('success-code').textContent = data.code;
          document.getElementById('success-ticket-link').href = '/reservation/ticket?code=' + encodeURIComponent(data.code);
          successEl.classList.remove('hidden');
          setTimeout(() => successEl.classList.add('hidden'), 15000);
        } else if (res.status === 422 && data.errors) {
          showErrors(data.errors);
        } else {
          errorsEl.textContent = 'Une erreur est survenue. Réessayez ou appelez-nous.';
          errorsEl.classList.remove('hidden');
        }
      } catch (err) {
        errorsEl.textContent = 'Connexion impossible. Vérifiez votre réseau et réessayez.';
        errorsEl.classList.remove('hidden');
      } finally {
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
        submitBtn.textContent = 'Confirmer ma réservation';
      }
    });

    // Afficher les erreurs de session après un POST non-AJAX
<?php if (!empty($reservationErrors)): ?>
    showErrors(<?= json_encode($reservationErrors, JSON_UNESCAPED_UNICODE) ?>);
<?php endif; ?>

    lucide.createIcons();
  </script>
</body>
</html>
