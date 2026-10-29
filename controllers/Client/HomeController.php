<?php

class HomeController extends Controller
{
    public function index(): void
    {
        $config = require CONFIG_PATH . '/app.php';
        $settings = SettingModel::getAll();
        $featured = (new ProductModel())->getFeatured();
        $categories = (new CategoryModel())->getActive();

        $data = compact('config', 'settings', 'featured', 'categories');
        $this->view->renderClient('client/home', $data);
    }
}
