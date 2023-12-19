<template>
	<Card
		title="Quyền của nhóm"
		subtitle="Tạo một nhóm hoặc quyền và gán nó cho các thành viên trong đội của bạn"
	>
		<template #actions>
			<Button v-if="showManageTeamButton" @click="showAddGroupDialog = true">
				Thêm nhóm mới
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
		@close="showEditMemberDialog = false"
	/>

	<ManageGroupMembers
		v-model:group="group"
		:show="showGroupMemberDialog"
		@close="showGroupMemberDialog = false"
	/>

	<Dialog
		:options="{
			title: 'Thêm nhóm mới',
			actions: [
				{
					label: 'Tạo nhóm',
					variant: 'solid',
					loading: $resources.addGroup.loading,
					onClick: () => $resources.addGroup.submit({ title: groupName })
				}
			]
		}"
		v-model="showAddGroupDialog"
	>
		<template v-slot:body-content>
			<Input :label="'Title'" type="text" v-model="groupName" required />
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
					title: 'Lời mời đã được gửi!',
					message:
						'Họ sẽ nhận được một email trong thời gian ngắn để tham gia vào đội của bạn.',
					color: 'green',
					icon: 'check'
				});
			}
		},
		addGroup: {
			url: 'press.api.account.add_permission_group',
			validate() {
				if (this.groupName.length == 0) {
					return 'Tên nhóm không được để trống.';
				}
			},
			onSuccess(r) {
				this.$resources.groups.fetch();
				notify({
					title: 'Nhóm đã được tạo!',
					message:
						'Bạn có thể gán nhóm này cho các thành viên trong đội của bạn ngay bây giờ',
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
					title: 'Nhóm đã bị xóa!',
					message: 'Quyền đã được loại bỏ khỏi tất cả các thành viên trong đội',
					color: 'green',
					icon: 'check'
				});
			}
		}
	},
	methods: {
		removeGroup(group) {
			this.$confirm({
				title: 'Xóa nhóm',
				message: `Bạn có chắc chắn muốn xóa ${group.title} ?`,
				actionLabel: 'Xóa',
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
					label: 'Quản lý thành viên',
					icon: 'users',
					onClick: () => {
						this.group = group;
						this.showGroupMemberDialog = true;
					}
				},
				{
					label: 'Chỉnh sửa quyền',
					icon: 'edit',
					onClick: () => {
						this.group = group;
						this.showEditMemberDialog = true;
					}
				},
				{
					label: 'Xóa',
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
