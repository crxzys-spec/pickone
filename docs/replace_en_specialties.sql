-- Auto-generated from 新通用.txt on 2026-01-27 08:56:15
-- Replaces the EN (通用类) subtree in specialties with the new hierarchy

BEGIN;

-- Remove old EN subtree mappings (optional but recommended)
-- MySQL 5.7 compatible: expand the tree up to 6 levels (current dataset depth).
DELETE FROM expert_specialties WHERE specialty_id IN (
    SELECT id FROM (
        SELECT id FROM specialties WHERE code = 'EN' OR name = '通用类'
        UNION ALL
        SELECT s1.id
        FROM specialties s1
        JOIN specialties p0 ON s1.parent_id = p0.id
        WHERE p0.code = 'EN' OR p0.name = '通用类'
        UNION ALL
        SELECT s2.id
        FROM specialties s2
        JOIN specialties s1 ON s2.parent_id = s1.id
        JOIN specialties p0 ON s1.parent_id = p0.id
        WHERE p0.code = 'EN' OR p0.name = '通用类'
        UNION ALL
        SELECT s3.id
        FROM specialties s3
        JOIN specialties s2 ON s3.parent_id = s2.id
        JOIN specialties s1 ON s2.parent_id = s1.id
        JOIN specialties p0 ON s1.parent_id = p0.id
        WHERE p0.code = 'EN' OR p0.name = '通用类'
        UNION ALL
        SELECT s4.id
        FROM specialties s4
        JOIN specialties s3 ON s4.parent_id = s3.id
        JOIN specialties s2 ON s3.parent_id = s2.id
        JOIN specialties s1 ON s2.parent_id = s1.id
        JOIN specialties p0 ON s1.parent_id = p0.id
        WHERE p0.code = 'EN' OR p0.name = '通用类'
        UNION ALL
        SELECT s5.id
        FROM specialties s5
        JOIN specialties s4 ON s5.parent_id = s4.id
        JOIN specialties s3 ON s4.parent_id = s3.id
        JOIN specialties s2 ON s3.parent_id = s2.id
        JOIN specialties s1 ON s2.parent_id = s1.id
        JOIN specialties p0 ON s1.parent_id = p0.id
        WHERE p0.code = 'EN' OR p0.name = '通用类'
    ) AS tmp_en_ids
);

-- Remove old EN subtree
DELETE FROM specialties WHERE id IN (
    SELECT id FROM (
        SELECT id FROM specialties WHERE code = 'EN' OR name = '通用类'
        UNION ALL
        SELECT s1.id
        FROM specialties s1
        JOIN specialties p0 ON s1.parent_id = p0.id
        WHERE p0.code = 'EN' OR p0.name = '通用类'
        UNION ALL
        SELECT s2.id
        FROM specialties s2
        JOIN specialties s1 ON s2.parent_id = s1.id
        JOIN specialties p0 ON s1.parent_id = p0.id
        WHERE p0.code = 'EN' OR p0.name = '通用类'
        UNION ALL
        SELECT s3.id
        FROM specialties s3
        JOIN specialties s2 ON s3.parent_id = s2.id
        JOIN specialties s1 ON s2.parent_id = s1.id
        JOIN specialties p0 ON s1.parent_id = p0.id
        WHERE p0.code = 'EN' OR p0.name = '通用类'
        UNION ALL
        SELECT s4.id
        FROM specialties s4
        JOIN specialties s3 ON s4.parent_id = s3.id
        JOIN specialties s2 ON s3.parent_id = s2.id
        JOIN specialties s1 ON s2.parent_id = s1.id
        JOIN specialties p0 ON s1.parent_id = p0.id
        WHERE p0.code = 'EN' OR p0.name = '通用类'
        UNION ALL
        SELECT s5.id
        FROM specialties s5
        JOIN specialties s4 ON s5.parent_id = s4.id
        JOIN specialties s3 ON s4.parent_id = s3.id
        JOIN specialties s2 ON s3.parent_id = s2.id
        JOIN specialties s1 ON s2.parent_id = s1.id
        JOIN specialties p0 ON s1.parent_id = p0.id
        WHERE p0.code = 'EN' OR p0.name = '通用类'
    ) AS tmp_en_ids
);

-- Insert new EN subtree
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) VALUES (NULL, '通用类', 'EN', 1, 1);
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '工程类', 'ENA', 1, 1 FROM specialties WHERE code = 'EN';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '工程咨询', 'ENA01', 1, 1 FROM specialties WHERE code = 'ENA';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '规划', 'ENA0101', 1, 1 FROM specialties WHERE code = 'ENA01';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '勘察', 'ENA0102', 1, 2 FROM specialties WHERE code = 'ENA01';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '设计', 'ENA0103', 1, 3 FROM specialties WHERE code = 'ENA01';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '工程造价', 'ENA0104', 1, 4 FROM specialties WHERE code = 'ENA01';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '工程管理', 'ENA02', 1, 2 FROM specialties WHERE code = 'ENA';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '监理', 'ENA0201', 1, 1 FROM specialties WHERE code = 'ENA02';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '项目管理(含代建)', 'ENA0202', 1, 2 FROM specialties WHERE code = 'ENA02';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '工程施工', 'ENA03', 1, 3 FROM specialties WHERE code = 'ENA';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '建筑工程', 'ENA0301', 1, 1 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '市政工程', 'ENA0302', 1, 2 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '公路工程', 'ENA0303', 1, 3 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '铁路工程', 'ENA0304', 1, 4 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '城市轨道交通工程', 'ENA0305', 1, 5 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '民航工程', 'ENA0306', 1, 6 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '水运工程', 'ENA0307', 1, 7 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '水利工程', 'ENA0308', 1, 8 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '水电工程', 'ENA0309', 1, 9 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '电力工程', 'ENA0310', 1, 10 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '新能源工程', 'ENA0311', 1, 11 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '矿山工程', 'ENA0312', 1, 12 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '石油天然气工程', 'ENA0313', 1, 13 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '机械工程', 'ENA0314', 1, 14 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '冶金工程', 'ENA0315', 1, 15 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '化工、医药工程', 'ENA0316', 1, 16 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '轻工业工程', 'ENA0317', 1, 17 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '农业工程', 'ENA0318', 1, 18 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '林业工程', 'ENA0319', 1, 19 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '商物粮工程', 'ENA0320', 1, 20 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '电子工程', 'ENA0321', 1, 21 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '通信工程', 'ENA0322', 1, 22 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '广播电影电视工程', 'ENA0323', 1, 23 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '海洋工程', 'ENA0324', 1, 24 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '建材工业工程', 'ENA0325', 1, 25 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '军工工程', 'ENA0326', 1, 26 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '生物工程', 'ENA0327', 1, 27 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '航空航天工程', 'ENA0328', 1, 28 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '地质环境', 'ENA0329', 1, 29 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '园林绿化工程', 'ENA0330', 1, 30 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '核工程', 'ENA0331', 1, 31 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '信息工程', 'ENA0332', 1, 32 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '文物保护工程', 'ENA0333', 1, 33 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '土地整治工程', 'ENA0334', 1, 34 FROM specialties WHERE code = 'ENA03';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '其他工程', 'ENA04', 1, 4 FROM specialties WHERE code = 'ENA';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '货物类', 'ENB', 1, 2 FROM specialties WHERE code = 'EN';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '机电产品类', 'ENB01', 1, 1 FROM specialties WHERE code = 'ENB';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '医疗器材', 'ENB02', 1, 2 FROM specialties WHERE code = 'ENB';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '金属材料', 'ENB03', 1, 3 FROM specialties WHERE code = 'ENB';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '石油及其制品', 'ENB04', 1, 4 FROM specialties WHERE code = 'ENB';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '煤炭煤层气及其制品', 'ENB05', 1, 5 FROM specialties WHERE code = 'ENB';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '化工材料及其制品', 'ENB06', 1, 6 FROM specialties WHERE code = 'ENB';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '建筑材料', 'ENB07', 1, 7 FROM specialties WHERE code = 'ENB';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '医药', 'ENB08', 1, 8 FROM specialties WHERE code = 'ENB';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '其他类', 'ENB09', 1, 9 FROM specialties WHERE code = 'ENB';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '服务类', 'ENC', 1, 3 FROM specialties WHERE code = 'EN';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '勘查与调查', 'ENC01', 1, 1 FROM specialties WHERE code = 'ENC';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '公共咨询', 'ENC02', 1, 2 FROM specialties WHERE code = 'ENC';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '经济管理', 'ENC03', 1, 3 FROM specialties WHERE code = 'ENC';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '工商管理', 'ENC04', 1, 4 FROM specialties WHERE code = 'ENC';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '金融', 'ENC05', 1, 5 FROM specialties WHERE code = 'ENC';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '法律', 'ENC06', 1, 6 FROM specialties WHERE code = 'ENC';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '运维、评估与修理', 'ENC07', 1, 7 FROM specialties WHERE code = 'ENC';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '租赁', 'ENC08', 1, 8 FROM specialties WHERE code = 'ENC';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '交通运输与物流', 'ENC09', 1, 9 FROM specialties WHERE code = 'ENC';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '节能服务', 'ENC10', 1, 10 FROM specialties WHERE code = 'ENC';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '高新技术服务', 'ENC11', 1, 11 FROM specialties WHERE code = 'ENC';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '其他服务', 'ENC12', 1, 12 FROM specialties WHERE code = 'ENC';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '应对气候变化服务', 'ENC13', 1, 13 FROM specialties WHERE code = 'ENC';
INSERT INTO specialties (parent_id, name, code, is_active, sort_order) SELECT id, '网络、电磁空间安全服务', 'ENC14', 1, 14 FROM specialties WHERE code = 'ENC';

COMMIT;