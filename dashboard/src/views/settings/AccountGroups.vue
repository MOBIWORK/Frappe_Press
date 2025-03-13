<template>
	<Card
		:title="$t('group_permissions')"
		:subtitle="$t('accountgroups_content_1')"
	>
		<template #actions>
			<Button v-if="showManageTeamButton" @click="showAddGroupDialog = true">
				{{ $t('add_new_group') }}
			</Button>
		</template>
		<div class="max-h-96 divide-y">
			<ListItem
				v-for="group in groups"
				:title="group.title"
				:description="group.name"
				:key="group.name"
			>
				<template #actions>
					<Dropdown :options="dropdownItems(group)" right>
						<template v-slot="{ open }">
							<Button icon="more-horizontal" />
						</template>
					</Dropdown>
				</template>
			</ListItem>
		</div>
	</Card>

	<EditPermissions
		:type="'group'"
		:show="showEditMemberDialog"
		:name="group.name"
		:title="group.title"
		@close="showEditMemberDialog = false"
	/>

	<ManageGroupMembers
		v-model:group="group"
		:show="showGroupMemberDialog"
		@close="showGroupMemberDialog = false"
	/>

	<Dialog
		:options="{
			title: $t('add_new_group'),
			actions: [
				{
					label: $t('create_group'),
					variant: 'solid',
					loading: $resources.addGroup.loading,
					onClick: () => $resources.addGroup.submit({ title: groupName })
				}
			]
		}"
		v-model="showAddGroupDialog"
	>
		<template v-slot:body-content>
			<Input :label="$t('title')" type="text" v-model="groupName" required />
			<ErrorMessage class="mt-2" :message="$resources.addGroup.error" />
		</template>
	</Dialog>
</template>
<script>
import EditPermissions from './EditPermissions.vue';
import ManageGroupMembers from './ManageGroupMembers.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'AccountGroups',
	components: {
		EditPermissions,
		ManageGroupMembers
	},
	data() {
		return {
			groupName: '',
			memberEmail: '',
			showAddGroupDialog: false,
			showGroupMemberDialog: false,
			showManageMemberDialog: false,
			showEditMemberDialog: false,
			group: { name: '', title: '' },
			showAddMemberForm: false
		};
	},
	resources: {
		groups: {
			url: 'press.api.account.groups',
			auto: true
		},
		addMember: {
			url: 'press.api.account.add_team_member',
			onSuccess() {
				this.showManageMemberDialog = false;
				this.memberEmail = null;
				notify({
					title: this.$t('invite_sent'),
					message: this.$t('accountmembers_content_3'),
					color: 'green',
					icon: 'check'
				});
			}
		},
		addGroup: {
			url: 'press.api.account.add_permission_group',
			validate() {
				if (this.groupName.length == 0) {
					return this.$t('group_name_is_required');
				}
			},
			onSuccess(r) {
				this.$resources.groups.fetch();
				notify({
					title: this.$t('group_created'),
					message: this.$t('accountgroups_content_2'),
					color: 'green',
					icon: 'check'
				});
				this.group = r;
				this.showAddGroupDialog = false;
				this.showGroupMemberDialog = true;
			}
		},
		removeGroup: {
			url: 'press.api.account.remove_permission_group',
			onSuccess() {
				this.$resources.groups.fetch();
				notify({
					title: this.$t('group_removed'),
					message: this.$t('accountgroups_content_3'),
					color: 'green',
					icon: 'check'
				});
			}
		}
	},
	methods: {
		removeGroup(group) {
			this.$confirm({
				title: this.$t('remove_group'),
				message: `${this.$t('are_you_sure_you_want_to_remove')} ${
					group.title
				} ?`,
				actionLabel: this.$t('remove'),
				actionColor: 'red',
				action: closeDialog => {
					this.$resources.removeGroup.submit({ name: group.name });
					closeDialog();
				}
			});
		},
		dropdownItems(group) {
			return [
				{
					label: this.$t('manage_members'),
					icon: 'users',
					onClick: () => {
						this.group = group;
						this.showGroupMemberDialog = true;
					}
				},
				{
					label: this.$t('edit_permissions'),
					icon: 'edit',
					onClick: () => {
						this.group = group;
						this.showEditMemberDialog = true;
					}
				},
				{
					label: this.$t('remove'),
					icon: 'trash-2',
					onClick: () => this.removeGroup(group)
				}
			];
		}
	},
	computed: {
		showManageTeamButton() {
			const team = this.$account.team;
			let show = this.$account.hasRole('Press Admin');
			return (
				show &&
				(team.default_payment_method ||
					team.payment_mode == 'Prepaid Credits' ||
					team.free_account ||
					team.erpnext_partner ||
					team.parent_team)
			);
		},
		groups() {
			if (!this.$resources.groups.data) return [];
			return this.$resources.groups.data;
		}
	}
};
</script>
