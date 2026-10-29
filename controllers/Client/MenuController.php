<?php

class ClientMenuController extends Controller
{
    public function index(): void
    {
        $config = require CONFIG_PATH . '/app.php';
        $settings = SettingModel::getAll();
        $categories = (new CategoryModel())->getActive();
        $products = (new ProductModel())->getAvailable();

        $grouped = [];
        foreach ($products as $product) {
            $catName = $product['category_name'];
            $grouped[$catName][] = $product;
        }

        $data = compact('config', 'settings', 'categories', 'products', 'grouped');
        $this->view->renderClient('client/menu', $data);
    }
}
