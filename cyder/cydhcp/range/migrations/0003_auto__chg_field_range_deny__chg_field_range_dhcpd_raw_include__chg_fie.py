# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Range.deny'
        db.alter_column('range', 'deny', self.gf('django.db.models.fields.CharField')(default='', max_length=20))

        # Changing field 'Range.dhcpd_raw_include'
        db.alter_column('range', 'dhcpd_raw_include', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Range.allow'
        db.alter_column('range', 'allow', self.gf('django.db.models.fields.CharField')(default='', max_length=20))

    def backwards(self, orm):

        # Changing field 'Range.deny'
        db.alter_column('range', 'deny', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'Range.dhcpd_raw_include'
        db.alter_column('range', 'dhcpd_raw_include', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Range.allow'
        db.alter_column('range', 'allow', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

    models = {
        'network.network': {
            'Meta': {'unique_together': "(('ip_upper', 'ip_lower', 'prefixlen'),)", 'object_name': 'Network', 'db_table': "'network'"},
            'dhcpd_raw_include': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_lower': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'}),
            'ip_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'ip_upper': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True'}),
            'network_str': ('django.db.models.fields.CharField', [], {'max_length': '49'}),
            'prefixlen': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['site.Site']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'vlan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vlan.Vlan']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'range.range': {
            'Meta': {'unique_together': "(('start_upper', 'start_lower', 'end_upper', 'end_lower'),)", 'object_name': 'Range', 'db_table': "'range'"},
            'allow': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'deny': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'dhcp_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'dhcpd_raw_include': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end_lower': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'end_str': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'end_upper': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'is_reserved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['network.Network']", 'null': 'True', 'blank': 'True'}),
            'range_type': ('django.db.models.fields.CharField', [], {'default': "'st'", 'max_length': '2'}),
            'start_lower': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'start_str': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'start_upper': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'})
        },
        'range.rangekeyvalue': {
            'Meta': {'unique_together': "(('key', 'value', 'range'),)", 'object_name': 'RangeKeyValue', 'db_table': "'range_kv'"},
            'has_validator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_option': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_quoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_statement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'range': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['range.Range']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'site.site': {
            'Meta': {'unique_together': "(('name', 'parent'),)", 'object_name': 'Site', 'db_table': "'site'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['site.Site']", 'null': 'True', 'blank': 'True'})
        },
        'vlan.vlan': {
            'Meta': {'unique_together': "(('name', 'number'),)", 'object_name': 'Vlan', 'db_table': "'vlan'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['range']