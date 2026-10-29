<?php
require __DIR__.'/lib.php';
$U=$_SESSION['u']??null;$p=$_GET['p']??'';$msg=$_SESSION['f']??'';unset($_SESSION['f']);
function home(){return ['cuisinier'=>'?p=kitchen','guichet'=>'?p=pos'][$_SESSION['u']['role']]??'?p=dashboard';}
if($_SERVER['REQUEST_METHOD']=='POST'){
 $a=$_POST['a']??'';
 try{
  if(!hash_equals(tok(),$_POST['_t']??''))throw new Exception('Jeton CSRF invalide');
  if($a=='login'){
   if(!trim($_POST['email']??'')||!($_POST['password']??''))throw new Exception('Veuillez remplir tous les champs');
   $u=one("SELECT * FROM users WHERE email=? AND is_active=1",[trim($_POST['email'])]);
   if(!$u||!password_verify($_POST['password'],$u['password']))throw new Exception('Email ou mot de passe incorrect');
   session_regenerate_id(true);$_SESSION['u']=$u;q("UPDATE users SET last_login=NOW() WHERE id=?",[$u['id']]);go(home());
  }
  if(!$U)throw new Exception('Connexion requise');
  switch($a){
   case 'pos':need('pos');$n=newOrder(json_decode($_POST['items'],true)?:[],$_POST['type'],$_POST['table_id']??0,$_POST['notes']??'');$_SESSION['f']="Commande $n créée";break;
   case 'status':need('orders');setStatus((int)$_POST['id'],$_POST['status']);break;
   case 'pay':need('orders');pay((int)$_POST['id'],$_POST['amount'],$_POST['method'],$_POST['phone']??'');break;
   case 'stock':need('stock');stockMove((int)$_POST['i'],$_POST['type'],(float)$_POST['qty'],$_POST['reason']);break;
   case 'toggle':need('menu');q("UPDATE products SET is_available=1-is_available WHERE id=?",[(int)$_POST['id']]);break;
   case 'tstatus':need('tables');q("UPDATE tables_restaurant SET status=? WHERE id=?",[$_POST['status'],(int)$_POST['id']]);break;
   case 'copen':need('cash');if(one("SELECT id FROM cash_registers WHERE status='open'"))throw new Exception('Une caisse est déjà ouverte');if(!is_numeric($_POST['amount']))throw new Exception('Montant invalide');q("INSERT INTO cash_registers(user_id,opening_amount) VALUES(?,?)",[$U['id'],$_POST['amount']]);break;
   case 'cmove':need('cash');$r=one("SELECT id FROM cash_registers WHERE status='open'");if(!$r)throw new Exception('Caisse fermée');if(!is_numeric($_POST['amount'])||trim($_POST['reason'])==='')throw new Exception('Montant et motif obligatoires');$in=$_POST['type']=='in';
    q("UPDATE cash_registers SET ".($in?"total_cash_in=total_cash_in+?":"total_cash_out=total_cash_out+?")." WHERE id=?",[$_POST['amount'],$r['id']]);
    q("INSERT INTO cash_movements(cash_register_id,type,amount,reason,created_by) VALUES(?,?,?,?,?)",[$r['id'],$in?'in':'out',$_POST['amount'],$_POST['reason'],$U['id']]);break;
   case 'cclose':need('cash');$r=one("SELECT * FROM cash_registers WHERE status='open'");if(!$r)throw new Exception('Aucune caisse ouverte');if(!is_numeric($_POST['counted']))throw new Exception('Montant invalide');
    q("UPDATE cash_registers SET closing_amount=?,expected_amount=?,closed_at=NOW(),status='closed',notes=? WHERE id=?",[$_POST['counted'],$r['opening_amount']+$r['total_cash_in']-$r['total_cash_out'],$_POST['notes'],$r['id']]);break;
  }
 }catch(Throwable $x){$_SESSION['f']=$x->getMessage();}
 go($_POST['back']??'?');
}
if($p=='logout'){session_destroy();go('?');}
function layout($t,$f){global $U,$msg;$nav=['dashboard'=>'Dashboard','pos'=>'POS','orders'=>'Commandes','kitchen'=>'Cuisine','tables'=>'Tables','stock'=>'Stock','menu'=>'Menu','cash'=>'Caisse'];
 echo '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>'.e($t).' — ADAM</title><style>*{box-sizing:border-box}body{margin:0;font:14px system-ui;background:#f5f6fa;display:flex;min-height:100vh}nav{width:200px;background:#1a1a2e;color:#fff;padding:16px;flex:none}nav b{display:block;margin-bottom:16px;color:#e94560;font-size:18px}nav a{display:block;color:#ccd;padding:8px;text-decoration:none;border-radius:6px}nav a:hover{background:#e94560;color:#fff}main{flex:1;padding:20px;overflow:auto}.c{background:#fff;border-radius:10px;padding:14px;margin-bottom:14px;box-shadow:0 1px 4px #0001}.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}table{width:100%;border-collapse:collapse}td,th{padding:6px;border-bottom:1px solid #eee;text-align:left}button,.b{background:#e94560;color:#fff;border:0;padding:7px 12px;border-radius:6px;cursor:pointer}input,select,textarea{padding:6px;border:1px solid #ccc;border-radius:6px}.m{background:#fff3cd;padding:10px;border-radius:6px;margin-bottom:12px}.k{font-size:22px;font-weight:700}.lo{color:#c00;font-weight:700}form.i{display:inline}@media(max-width:700px){body{display:block}nav{width:auto}}</style><nav><b>ADAM</b>';
 foreach($nav as $k=>$l)if(can($k))echo '<a href="?p='.$k.'">'.$l.'</a>';
 echo '<a href="?p=logout">Déconnexion ('.e($U['name']).')</a></nav><main>'.($msg?'<div class=m>'.e($msg).'</div>':'').'<h2>'.e($t).'</h2>';$f();echo '</main>';}
if(!$U){
 if($p=='login'){echo '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><body style="font:14px system-ui;background:#1a1a2e;display:grid;place-items:center;height:100vh"><form method=post style="background:#fff;padding:28px;border-radius:12px;width:300px;display:grid;gap:10px"><h2 style="margin:0;color:#e94560">Restaurant ADAM</h2>'.($msg?'<div style="color:#c00">'.e($msg).'</div>':'').csrf().'<input type=hidden name=a value=login><input name=email placeholder=Email><input name=password type=password placeholder="Mot de passe"><button style="padding:10px">Connexion</button></form>';exit;}
 $cats=all("SELECT * FROM categories WHERE is_active=1 ORDER BY sort_order");
 echo '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Restaurant ADAM</title><body style="font:15px system-ui;max-width:860px;margin:auto;padding:16px"><h1 style="color:#e94560">Restaurant ADAM</h1><a href="?p=login">Connexion équipe</a>';
 foreach($cats as $c){echo '<h3>'.e($c['name']).'</h3>';foreach(all("SELECT * FROM products WHERE category_id=? AND is_available=1",[$c['id']]) as $r)echo '<div style="display:flex;justify-content:space-between;border-bottom:1px solid #eee;padding:4px"><span>'.e($r['name']).'</span><b>'.fc($r['price']).'</b></div>';}
 echo '<h2>Réserver une table</h2><form id=r style="display:grid;gap:8px;max-width:340px"><input name=customer_name placeholder=Nom required><input name=customer_phone placeholder=Téléphone required><input name=customer_email placeholder=Email><input type=date name=date required><input type=time name=time required><input type=number name=guests min=1 max=10 value=2 required><button>Réserver</button></form><p id=o></p><script>r.onsubmit=async v=>{v.preventDefault();let x=await fetch("api/reservation.php",{method:"POST",body:JSON.stringify(Object.fromEntries(new FormData(r)))});let j=await x.json();o.textContent=j.code?j.message+" — code "+j.code+" — table : "+j.table:j.error}</script>';exit;}
if($p===''||!can($p))if($p==='')go(home());else{http_response_code(403);layout('Accès refusé',function(){echo 'Permission insuffisante.';});exit;}
$st=['pending','confirmed','preparing','ready','served','paid','cancelled'];
$pages=[
'dashboard'=>function(){
 $a=one("SELECT COUNT(*) n,COALESCE(SUM(status='paid')*0,0) z FROM orders WHERE DATE(created_at)=CURDATE()")['n'];
 $ca=one("SELECT COALESCE(SUM(total),0) s FROM orders WHERE status='paid' AND DATE(paid_at)=CURDATE()")['s'];
 $to=one("SELECT COUNT(*) n FROM tables_restaurant WHERE status='occupied'")['n'];$rs=one("SELECT COUNT(*) n FROM reservations WHERE date=CURDATE()")['n'];
 $low=all("SELECT * FROM ingredients WHERE current_stock<=min_stock");
 echo "<div class=g><div class=c>Commandes du jour<div class=k>$a</div></div><div class=c>CA payé<div class=k>".fc($ca)."</div></div><div class=c>Tables occupées<div class=k>$to</div></div><div class=c>Réservations<div class=k>$rs</div></div><div class=c>Stock bas<div class=k>".count($low)."</div></div></div>";
 echo '<div class=c><b>Alertes stock</b><br>';foreach($low as $l)echo e($l['name']).' : '.$l['current_stock'].' '.e($l['unit']).'<br>';
 echo '</div><div class=c><b>Dernières commandes</b><table>';foreach(all("SELECT * FROM orders ORDER BY id DESC LIMIT 8") as $o)echo '<tr><td>'.e($o['order_number']).'<td>'.e($o['status']).'<td>'.fc($o['total']);echo '</table></div>';},
'pos'=>function(){
 $pr=all("SELECT id,name,price FROM products WHERE is_available=1 ORDER BY category_id,name");$tb=all("SELECT id,name FROM tables_restaurant WHERE status IN('free','occupied')");
 echo '<div class=g style="grid-template-columns:2fr 1fr;align-items:start"><div class=g>';foreach($pr as $x)echo '<div class=c style="cursor:pointer" onclick="add('.$x['id'].')"><b>'.e($x['name']).'</b><br>'.fc($x['price']).'</div>';
 echo '</div><form class=c method=post>'.csrf().'<input type=hidden name=a value=pos><input type=hidden name=items id=it><div id=cart></div><p>Sous-total <b id=st></b><br>Taxe 18 % <b id=tx></b><br>Total <b id=tt></b></p><select name=type><option value=dine_in>Sur place<option value=takeaway>À emporter</select> <select name=table_id><option value=0>— table —'.implode('',array_map(fn($t)=>'<option value='.$t['id'].'>'.e($t['name']),$tb)).'</select><br><br><textarea name=notes placeholder=Notes style="width:100%"></textarea><button>Créer la commande</button></form></div>';
 echo '<script>const P='.json_encode($pr).';let C={};function add(i){C[i]=(C[i]||0)+1;d()}function d(){let s=0,h="";for(let i in C){let p=P.find(x=>x.id==i);s+=p.price*C[i];h+=`<div>${p.name} <button type=button onclick="C[${i}]--;if(!C[${i}])delete C[${i}];d()">−</button> ${C[i]} <button type=button onclick="add(${i})">+</button></div>`}cart.innerHTML=h;let t=Math.round(s*.18*100)/100;st.textContent=s;tx.textContent=t;tt.textContent=s+t;it.value=JSON.stringify(Object.keys(C).map(i=>({id:i,q:C[i]})))}d()</script>';},
'orders'=>function(){global $st;
 foreach(all("SELECT o.*,t.name tn,(SELECT COALESCE(SUM(amount),0) FROM payments WHERE order_id=o.id AND status='completed') paid FROM orders o LEFT JOIN tables_restaurant t ON t.id=o.table_id ORDER BY o.id DESC LIMIT 40") as $o){
  echo '<div class=c><b>'.e($o['order_number']).'</b> — '.e($o['type']).' '.e($o['tn']).' — <b>'.e($o['status']).'</b> — '.fc($o['total']).' (payé '.fc($o['paid']).')<br>';
  foreach(all("SELECT i.quantity,p.name FROM order_items i JOIN products p ON p.id=i.product_id WHERE order_id=?",[$o['id']]) as $i)echo $i['quantity'].'× '.e($i['name']).'; ';
  echo '<br><form class=i method=post>'.csrf().'<input type=hidden name=a value=status><input type=hidden name=id value='.$o['id'].'><input type=hidden name=back value="?p=orders"><select name=status>';foreach($st as $s)echo '<option'.($s==$o['status']?' selected':'').'>'.$s;echo '</select> <button>Statut</button></form>';
  if(can('cash')&&!in_array($o['status'],['paid','cancelled']))echo ' <form class=i method=post>'.csrf().'<input type=hidden name=a value=pay><input type=hidden name=id value='.$o['id'].'><input type=hidden name=back value="?p=orders"><input name=amount type=number step=any value='.($o['total']-$o['paid']).' style="width:90px"><select name=method><option value=cash>Espèces<option value=mobile_money>Mobile Money<option value=card>Carte</select><input name=phone placeholder=Tél style="width:90px"><button>Encaisser</button></form>';
  echo ' <a href="javascript:print()">Imprimer</a></div>';}},
'kitchen'=>function(){
 echo '<meta http-equiv=refresh content=15><div class=g>';
 foreach(all("SELECT * FROM orders WHERE status IN('confirmed','preparing') ORDER BY id") as $o){echo '<div class=c><b>'.e($o['order_number']).'</b> '.e($o['status']).'<br>';
  foreach(all("SELECT i.quantity,p.name FROM order_items i JOIN products p ON p.id=i.product_id WHERE order_id=?",[$o['id']]) as $i)echo $i['quantity'].'× '.e($i['name']).'<br>';
  $n=$o['status']=='confirmed'?'preparing':'ready';echo '<form method=post>'.csrf().'<input type=hidden name=a value=status><input type=hidden name=id value='.$o['id'].'><input type=hidden name=status value='.$n.'><input type=hidden name=back value="?p=kitchen"><button>→ '.$n.'</button></form></div>';}
 echo '</div>';},
'tables'=>function(){echo '<div class=g>';foreach(all("SELECT * FROM tables_restaurant ORDER BY number") as $t){echo '<div class=c><b>'.e($t['name']).'</b> ('.$t['capacity'].' pl., '.e($t['zone']).')<br><form method=post>'.csrf().'<input type=hidden name=a value=tstatus><input type=hidden name=id value='.$t['id'].'><input type=hidden name=back value="?p=tables"><select name=status>';foreach(['free','reserved','occupied','maintenance'] as $s)echo '<option'.($s==$t['status']?' selected':'').'>'.$s;echo '</select><button>OK</button></form></div>';}echo '</div>';},
'stock'=>function(){$ing=all("SELECT * FROM ingredients ORDER BY name");$v=0;
 echo '<div class=c><form method=post>'.csrf().'<input type=hidden name=a value=stock><input type=hidden name=back value="?p=stock"><select name=i>';foreach($ing as $g)echo '<option value='.$g['id'].'>'.e($g['name']);echo '</select><select name=type><option value=in>Entrée<option value=out>Sortie<option value=adjust>Ajustement (signé)</select><input name=qty type=number step=any placeholder=Quantité><input name=reason placeholder=Motif><button>Valider</button></form></div><div class=c><table><tr><th>Ingrédient<th>Stock<th>Seuil<th>Valeur';
 foreach($ing as $g){$v+=$g['current_stock']*$g['cost_per_unit'];echo '<tr><td>'.e($g['name']).'<td class="'.($g['current_stock']<=$g['min_stock']?'lo':'').'">'.(float)$g['current_stock'].' '.e($g['unit']).'<td>'.(float)$g['min_stock'].'<td>'.fc($g['current_stock']*$g['cost_per_unit']);}
 echo '</table><p>Valorisation : <b>'.fc($v).'</b></p></div><div class=c><b>Derniers mouvements</b><table>';foreach(all("SELECT m.*,g.name FROM inventory_movements m JOIN ingredients g ON g.id=m.ingredient_id ORDER BY m.id DESC LIMIT 15") as $m)echo '<tr><td>'.e($m['created_at']).'<td>'.e($m['name']).'<td>'.$m['type'].'<td>'.(float)$m['quantity'].'<td>'.e($m['reason']);echo '</table></div>';},
'menu'=>function(){echo '<div class=c><table>';foreach(all("SELECT p.*,c.name cn FROM products p JOIN categories c ON c.id=p.category_id ORDER BY c.sort_order,p.name") as $r)echo '<tr><td>'.e($r['name']).'<td>'.e($r['cn']).'<td>'.fc($r['price']).'<td><form method=post>'.csrf().'<input type=hidden name=a value=toggle><input type=hidden name=id value='.$r['id'].'><input type=hidden name=back value="?p=menu"><button>'.($r['is_available']?'Désactiver':'Activer').'</button></form>';echo '</table></div>';},
'cash'=>function(){$r=one("SELECT * FROM cash_registers WHERE status='open'");$b='<input type=hidden name=back value="?p=cash">';
 if(!$r)echo '<div class=c><b>Caisse fermée</b><form method=post>'.csrf().$b.'<input type=hidden name=a value=copen><input name=amount type=number step=any placeholder="Fond de caisse"><button>Ouvrir</button></form></div>';
 else{$ex=$r['opening_amount']+$r['total_cash_in']-$r['total_cash_out'];
  echo '<div class=c>Ouverte le '.e($r['opened_at']).' — fond '.fc($r['opening_amount']).' — entrées '.fc($r['total_cash_in']).' — sorties '.fc($r['total_cash_out']).' — <b>attendu '.fc($ex).'</b></div>
  <div class=c><form method=post>'.csrf().$b.'<input type=hidden name=a value=cmove><select name=type><option value=in>Entrée<option value=out>Sortie</select><input name=amount type=number step=any placeholder=Montant><input name=reason placeholder=Motif><button>Ajouter</button></form></div>
  <div class=c><form method=post>'.csrf().$b.'<input type=hidden name=a value=cclose><input name=counted type=number step=any placeholder="Montant compté"><input name=notes placeholder=Notes><button>Fermer la caisse</button></form></div>';}
 echo '<div class=c><b>Mouvements</b><table>';foreach(all("SELECT * FROM cash_movements ORDER BY id DESC LIMIT 20") as $m)echo '<tr><td>'.e($m['created_at']).'<td>'.$m['type'].'<td>'.fc($m['amount']).'<td>'.e($m['reason']);echo '</table></div>';}
];
layout(ucfirst($p),$pages[$p]);
