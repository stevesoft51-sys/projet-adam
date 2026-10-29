<?php

class AdminMenuController extends Controller
{
    private ProductModel $productModel;
    private CategoryModel $categoryModel;

    public function __construct()
    {
        parent::__construct();
        $this->productModel = new ProductModel();
        $this->categoryModel = new CategoryModel();
    }

    public function index(): void
    {
        AuthMiddleware::can('menu');
        $products = $this->productModel->getAdmin();
        $this->view->renderAdmin('admin/menu/index', compact('products'));
    }

    public function create(): void
    {
        AuthMiddleware::can('menu');
        $categories = $this->categoryModel->getAll();
        $ingredients = (new IngredientModel())->getAll();
        $this->view->renderAdmin('admin/menu/create', compact('categories', 'ingredients'));
    }

    public function store(): void
    {
        AuthMiddleware::can('menu');
        AuthMiddleware::csrf();

        $validated = $this->validate([
            'name' => 'required|max:150',
            'category_id' => 'required|integer',
            'price' => 'required|numeric',
            'cost_price' => 'numeric',
            'description' => 'max:500',
            'preparation_time' => 'integer',
        ]);

        $validated['is_available'] = isset($_POST['is_available']) ? 1 : 0;
        $validated['is_featured'] = isset($_POST['is_featured']) ? 1 : 0;
        $validated['sort_order'] = (int)($_POST['sort_order'] ?? 0);

        $image = $this->uploadImage('image', 'menu');
        if ($image) {
            $validated['image'] = $image;
        }

        $productId = $this->productModel->create($validated);

        if (!empty($_POST['ingredient_id'])) {
            $ingredients = [];
            foreach ($_POST['ingredient_id'] as $idx => $ingId) {
                $ingredients[] = [
                    'ingredient_id' => (int)$ingId,
                    'quantity' => (float)($_POST['ingredient_qty'][$idx] ?? 0),
                ];
            }
            $this->productModel->updateIngredients($productId, $ingredients);
        }

        $_SESSION['success'] = 'Produit ajouté avec succès';
        $this->redirect('/admin/menu');
    }

    public function edit(): void
    {
        AuthMiddleware::can('menu');
        $id = (int)$this->get('id');
        $product = $this->productModel->getWithIngredients($id);
        if (!$product) {
            $_SESSION['error'] = 'Produit introuvable';
            $this->redirect('/admin/menu');
        }
        $categories = $this->categoryModel->getAll();
        $ingredients = (new IngredientModel())->getAll();
        $this->view->renderAdmin('admin/menu/edit', compact('product', 'categories', 'ingredients'));
    }

    public function update(): void
    {
        AuthMiddleware::can('menu');
        AuthMiddleware::csrf();

        $id = (int)($_POST['id'] ?? 0);
        $validated = $this->validate([
            'name' => 'required|max:150',
            'category_id' => 'required|integer',
            'price' => 'required|numeric',
            'cost_price' => 'numeric',
            'description' => 'max:500',
            'preparation_time' => 'integer',
        ]);

        $validated['is_available'] = isset($_POST['is_available']) ? 1 : 0;
        $validated['is_featured'] = isset($_POST['is_featured']) ? 1 : 0;
        $validated['sort_order'] = (int)($_POST['sort_order'] ?? 0);

        $old = $this->productModel->find($id);
        $image = $this->uploadImage('image', 'menu');
        if ($image) {
            if ($old && $old['image']) {
                $this->deleteImage($old['image']);
            }
            $validated['image'] = $image;
        }

        $this->productModel->updateById($id, $validated);

        if (!empty($_POST['ingredient_id'])) {
            $ingredients = [];
            foreach ($_POST['ingredient_id'] as $idx => $ingId) {
                $ingredients[] = [
                    'ingredient_id' => (int)$ingId,
                    'quantity' => (float)($_POST['ingredient_qty'][$idx] ?? 0),
                ];
            }
            $this->productModel->updateIngredients($id, $ingredients);
        }

        $_SESSION['success'] = 'Produit mis à jour avec succès';
        $this->redirect('/admin/menu');
    }

    public function delete(): void
    {
        AuthMiddleware::can('menu');
        AuthMiddleware::csrf();

        $id = (int)($_POST['id'] ?? 0);
        $product = $this->productModel->find($id);
        if (!$product) {
            $_SESSION['error'] = 'Produit introuvable';
            $this->redirect('/admin/menu');
        }

        $orderCount = $this->db->count('order_items', 'product_id = ?', [$id]);
        if ($orderCount > 0) {
            $_SESSION['error'] = 'Ce produit a ' . $orderCount . ' commande(s) et ne peut pas être supprimé. Vous pouvez le désactiver à la place.';
            $this->redirect('/admin/menu');
        }

        if ($product['image']) {
            $this->deleteImage($product['image']);
        }
        $this->productModel->deleteById($id);

        $_SESSION['success'] = 'Produit supprimé';
        $this->redirect('/admin/menu');
    }

    public function toggle(): void
    {
        AuthMiddleware::can('menu');
        AuthMiddleware::csrf();

        $id = (int)($_POST['id'] ?? 0);
        $this->productModel->toggle($id);
        $this->json(['success' => true]);
    }

    public function categories(): void
    {
        AuthMiddleware::can('menu');
        $categories = $this->categoryModel->getAll();
        $this->view->renderAdmin('admin/menu/categories', compact('categories'));
    }

    public function storeCategory(): void
    {
        AuthMiddleware::can('menu');
        AuthMiddleware::csrf();

        $validated = $this->validate([
            'name' => 'required|max:100',
            'description' => 'max:500',
        ]);
        $validated['sort_order'] = (int)($_POST['sort_order'] ?? 0);

        $this->categoryModel->create($validated);
        $_SESSION['success'] = 'Catégorie ajoutée';
        $this->redirect('/admin/categories');
    }

    public function deleteCategory(): void
    {
        AuthMiddleware::can('menu');
        AuthMiddleware::csrf();

        $id = (int)($_POST['id'] ?? 0);
        $productCount = $this->db->count('products', 'category_id = ?', [$id]);
        if ($productCount > 0) {
            $_SESSION['error'] = "Cette catégorie contient {$productCount} produit(s) et ne peut pas être supprimée. Déplacez les produits d'abord.";
            $this->redirect('/admin/categories');
        }
        $this->categoryModel->deleteById($id);
        $_SESSION['success'] = 'Catégorie supprimée';
        $this->redirect('/admin/categories');
    }
}
