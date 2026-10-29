<?php
require __DIR__.'/../lib.php';header('Content-Type: application/json; charset=utf-8');
function out($c,$d){http_response_code($c);echo json_encode($d,JSON_UNESCAPED_UNICODE);exit;}
if($_SERVER['REQUEST_METHOD']=='GET'){$r=one("SELECT * FROM reservations WHERE code=?",[$_GET['code']??'']);$r?out(200,$r):out(404,['error'=>'Réservation introuvable']);}
$d=json_decode(file_get_contents('php://input'),true)?:$_POST;
foreach(['customer_name','customer_phone','date','time','guests'] as $f)if(empty($d[$f]))out(400,['error'=>"Champ obligatoire : $f"]);
$g=(int)$d['guests'];$dur=(int)($d['duration']??120);$s=strtotime($d['date'].' '.$d['time']);$e=$s+$dur*60;$tid=null;
foreach(all("SELECT * FROM tables_restaurant WHERE is_active=1 AND capacity>=? AND status NOT IN('reserved','occupied','maintenance') ORDER BY capacity,number",[$g]) as $t){
 $ok=true;foreach(all("SELECT time,duration FROM reservations WHERE table_id=? AND date=? AND status IN('pending','confirmed','seated')",[$t['id'],$d['date']]) as $r){$rs=strtotime($d['date'].' '.$r['time']);if($s<$rs+$r['duration']*60&&$e>$rs)$ok=false;}
 if($ok){$tid=$t['id'];$tn=$t['name'];break;}}
$code=strtoupper(substr(md5(uniqid('',true)),0,10));
q("INSERT INTO reservations(code,customer_name,customer_phone,customer_email,date,time,duration,guests,table_id,status,notes) VALUES(?,?,?,?,?,?,?,?,?,'confirmed',?)",[$code,$d['customer_name'],$d['customer_phone'],$d['customer_email']??'',$d['date'],$d['time'],$dur,$g,$tid,$d['notes']??'']);
if($tid)q("UPDATE tables_restaurant SET status='reserved' WHERE id=?",[$tid]);
out(201,['code'=>$code,'message'=>'Réservation confirmée','table'=>$tid?$tn:'À confirmer']);
