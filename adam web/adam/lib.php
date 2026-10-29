<?php
session_start();
$C=require __DIR__.'/config.php';
function db(){static $d;global $C;return $d??=new PDO("mysql:host={$C['host']};dbname={$C['db']};charset=utf8mb4",$C['user'],$C['pass'],[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC]);}
function q($s,$a=[]){$t=db()->prepare($s);$t->execute($a);return $t;}
function all($s,$a=[]){return q($s,$a)->fetchAll();}
function one($s,$a=[]){return q($s,$a)->fetch();}
function e($v){return htmlspecialchars((string)$v,ENT_QUOTES,'UTF-8');}
function fc($v){return number_format((float)$v,0,',',' ').' FCFA';}
function tok(){return $_SESSION['t']??=bin2hex(random_bytes(16));}
function csrf(){return '<input type=hidden name=_t value="'.tok().'">';}
function go($u){header("Location: $u");exit;}
$PERM=['manager'=>['dashboard','menu','stock','orders','order','kitchen','pos','tables','cash'],'serveur'=>['orders','order','kitchen','pos','tables','cash'],'cuisinier'=>['orders','order','kitchen'],'guichet'=>['pos','cash','orders','order']];
function can($p){$r=$_SESSION['u']['role']??'';return $r=='admin'||in_array($p,$GLOBALS['PERM'][$r]??[]);}
function need($p){if(!can($p))throw new Exception('Accès refusé');}
function setStatus($id,$s){
 $o=one("SELECT * FROM orders WHERE id=?",[$id]);if(!$o)throw new Exception('Commande introuvable');
 if($s=='confirmed')foreach(all("SELECT product_id,quantity FROM order_items WHERE order_id=?",[$id]) as $i)
  q("UPDATE ingredients g JOIN product_ingredients r ON r.ingredient_id=g.id SET g.current_stock=GREATEST(0,g.current_stock-r.quantity*?) WHERE r.product_id=?",[$i['quantity'],$i['product_id']]);
 q("UPDATE orders SET status=?".($s=='paid'?",paid_at=NOW()":"")." WHERE id=?",[$s,$id]);
 if($o['table_id']){$t=$s=='served'?'occupied':(in_array($s,['paid','cancelled'])?'free':null);if($t)q("UPDATE tables_restaurant SET status=? WHERE id=?",[$t,$o['table_id']]);}
}
function newOrder($items,$type,$tid,$notes){
 if(!$items)throw new Exception('Ajoutez au moins un article');
 $sub=0;$rows=[];foreach($items as $i){$p=one("SELECT * FROM products WHERE id=?",[(int)$i['id']]);$n=max(1,(int)$i['q']);if(!$p)continue;$rows[]=[$p,$n];$sub+=$p['price']*$n;}
 if(!$rows)throw new Exception('Articles invalides');
 $tax=round($sub*$GLOBALS['C']['tax']/100,2);$tid=$type=='dine_in'&&$tid?(int)$tid:null;
 $n=one("SELECT COUNT(*) c FROM orders WHERE DATE(created_at)=CURDATE()")['c']+1;$num='ORD-'.date('Ymd').'-'.sprintf('%04d',$n);
 q("INSERT INTO orders(order_number,table_id,user_id,type,status,subtotal,discount,tax,total,notes) VALUES(?,?,?,?,'confirmed',?,0,?,?,?)",[$num,$tid,$_SESSION['u']['id'],$type,$sub,$tax,$sub+$tax,$notes]);
 $id=db()->lastInsertId();
 foreach($rows as [$p,$n])q("INSERT INTO order_items(order_id,product_id,quantity,unit_price,total_price) VALUES(?,?,?,?,?)",[$id,$p['id'],$n,$p['price'],$p['price']*$n]);
 if($tid)q("UPDATE tables_restaurant SET status='occupied' WHERE id=?",[$tid]);
 return $num; // pas de déduction de stock ici (comportement voulu)
}
function pay($oid,$amt,$m,$phone){
 if(!is_numeric($amt)||$amt<=0)throw new Exception('Montant invalide');
 if(!in_array($m,['cash','mobile_money','card']))throw new Exception('Méthode invalide');
 $o=one("SELECT * FROM orders WHERE id=?",[$oid]);if(!$o)throw new Exception('Commande introuvable');
 $reg=one("SELECT id FROM cash_registers WHERE status='open'");
 q("INSERT INTO payments(order_id,amount,method,status,phone_number,cash_register_id,received_by) VALUES(?,?,?,'completed',?,?,?)",[$oid,$amt,$m,$phone,$reg['id']??null,$_SESSION['u']['id']]);
 if($reg){q("UPDATE cash_registers SET total_cash_in=total_cash_in+? WHERE id=?",[$amt,$reg['id']]); // quirk : tous modes
  q("INSERT INTO cash_movements(cash_register_id,type,amount,reason,reference,created_by) VALUES(?,'in',?,?,?,?)",[$reg['id'],$amt,'Paiement '.$o['order_number'],$o['order_number'],$_SESSION['u']['id']]);}
 $s=one("SELECT SUM(amount) s FROM payments WHERE order_id=? AND status='completed'",[$oid])['s'];
 if($s>=$o['total'])setStatus($oid,'paid');
}
function stockMove($iid,$type,$qty,$reason){
 $g=one("SELECT * FROM ingredients WHERE id=?",[$iid]);if(!$g)throw new Exception('Ingrédient introuvable');
 if(!is_numeric($qty)||$qty==0)throw new Exception('Quantité invalide');
 if(trim($reason)==='')throw new Exception('Motif obligatoire');
 if($type!='adjust'&&$qty<0)throw new Exception('Quantité négative interdite');
 $d=$type=='in'?$qty:($type=='out'?-$qty:$qty);$new=$g['current_stock']+$d;
 if($new<0)throw new Exception('Stock insuffisant');
 q("UPDATE ingredients SET current_stock=? WHERE id=?",[round($new,3),$iid]);
 q("INSERT INTO inventory_movements(ingredient_id,type,quantity,reason,created_by) VALUES(?,?,?,?,?)",[$iid,$type,$qty,$reason,$_SESSION['u']['id']]);
}
