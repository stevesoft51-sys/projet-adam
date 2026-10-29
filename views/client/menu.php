<?php $pageTitle = 'La Carte'; ?>
<section class="menu-hero">
    <div class="container">
        <h1>Notre Carte</h1>
        <p>Des saveurs authentiques pour chaque moment</p>
    </div>
</section>

<section class="section">
    <div class="container">
        <div class="menu-filters" id="menuFilters">
            <button class="filter-btn active" data-filter="all">Tout</button>
            <?php foreach ($categories as $cat): ?>
                <button class="filter-btn" data-filter="<?= $cat['id'] ?>"><?= htmlspecialchars($cat['name']) ?></button>
            <?php endforeach; ?>
        </div>

        <?php if (empty($grouped)): ?>
            <p class="text-center text-muted" style="padding:4rem 0">Le menu sera bientot disponible...</p>
        <?php else: ?>
            <?php foreach ($grouped as $catName => $catProducts): ?>
                <div class="menu-category-section" data-category="<?= $catProducts[0]['category_id'] ?>">
                    <h2 class="menu-category-title"><?= htmlspecialchars($catName) ?></h2>
                    <div class="menu-grid">
                        <?php foreach ($catProducts as $p): ?>
                            <div class="menu-card" data-category="<?= $p['category_id'] ?>">
                                <?php if ($p['image']): ?>
                                    <img src="<?= htmlspecialchars($p['image']) ?>" alt="<?= htmlspecialchars($p['name']) ?>" class="menu-card-img">
                                <?php else: ?>
                                    <div class="menu-card-img menu-placeholder"><i data-lucide="utensils"></i></div>
                                <?php endif; ?>
                                <div class="menu-card-body">
                                    <div class="menu-card-header">
                                        <h3><?= htmlspecialchars($p['name']) ?></h3>
                                        <span class="menu-card-price"><?= View::money($p['price']) ?></span>
                                    </div>
                                    <?php if ($p['description']): ?>
                                        <p class="menu-card-desc"><?= htmlspecialchars($p['description']) ?></p>
                                    <?php endif; ?>
                                    <?php if ($p['preparation_time']): ?>
                                        <span class="menu-card-time">~<?= $p['preparation_time'] ?> min</span>
                                    <?php endif; ?>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            <?php endforeach; ?>
        <?php endif; ?>
    </div>
</section>
