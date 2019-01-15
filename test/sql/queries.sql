--name
select p1.id as fb_id, p1.name as fb_name, p2.id as tw_id, p2.name as tw_name, p1.profile_url as fb_url, p2.profile_url as tw_url from (profiles p1, profiles p2) where 
p1.platform = 'Facebook' and p2.platform = 'Twitter' and 
p1.name = p2.name;

--name, location
select p1.id as fb_id, p1.name as fb_name, l1.name as fb_city, p2.id as tw_id, p2.name as tw_name, l2.name as tw_city, p1.profile_url as fb_url, p2.profile_url as tw_url from (profiles p1, profiles p2, locations l1, locations l2) where 
p1.platform = 'Facebook' and p2.platform = 'Twitter' and 
l1.profile_id = p1.id and l2.profile_id = p2.id and
p1.name = p2.name;