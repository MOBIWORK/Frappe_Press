<template>
	<Card
		title="Thành viên nhóm và quyền"
		subtitle="Các thành viên trong nhóm có thể thay mặt bạn truy cập vào tài khoản của bạn."
	>
		<template #actions>
			<Button
				v-if="showManageTeamButton"
				@click="showManageMemberDialog = true"
			>
				Thêm thành viên mới
			</Button>
		</template>
		<div class="max-h-96 divide-y">
			<ListItem
				v-for="member in $account.team_members"
				:title="`${member.first_name}`"
				:description="member.name"
				:key="member.name"
			>
				<template #actions>
					<Badge
						label="Owner"
						color="blue"
						class="ml-2"
						v-if="member.name == $account.team.user"
					/>
					<Dropdown v-else :options="dropdownItems(member)" right>
						<template v-slot="{ open }">
							<Button icon="more-horizontal" />
						</template>
					</Dropdown>
				</template>
			</ListItem>
		</div>

		<Dialog
			:options="{
				title: 'Thêm thành viên mới',
				actions: [
					{
						label: 'Gửi lời mời',
						variant: 'solid',
						loading: $resources.addMember.loading,
						onClick: () => $resources.addMember.submit({ email: memberEmail })
					}
				]
			}"
			v-model="showManageMemberDialog"
		>
			<template v-slot:body-content>
				<FormControl
					label="Nhập địa chỉ email của thành viên để mời họ."
					class="mt-2"
					v-model="memberEmail"
					required
				/>
				<ErrorMessage :message="$resources.addMember.error" />
			</template>
		</Dialog>
		<EditPermissions
			:type="'user'"
			:show="showEditMemberDialog"
			:name="memberName"
			@close="showEditMemberDialog = false"
		/>
	</Card>
</template>
<script>
import EditPermissions from './EditPermissions.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'AccountMembers',
	components: {
		EditPermissions
	},
	data() {
		return {
			showManageMemberDialog: false,
			showEditMemberDialog: false,
			memberName: '',
			showAddMemberForm: false,
			memberEmail: null
		};
	},
	resources: {
		addMember: {
			url: 'press.api.account.add_team_member',
			onSuccess() {
				this.showManageMemberDialog = false;
				this.memberEmail = null;
				notify({
					title: 'Lời mời đã được gửi!',
					message:
						'Họ sẽ nhận được một email trong thời gian ngắn để tham gia vào nhóm của bạn.',
					color: 'green',
					icon: 'check'
				});
			}
		},
		removeMember: {
			url: 'press.api.account.remove_team_member',
			onSuccess() {
				this.showManageMemberDialog = false;
				this.$account.fetchAccount();
				notify({
					title: 'Thành viên nhóm đã bị loại bỏ.',
					icon: 'check',
					color: 'green'
				});
			}
		}
	},
	methods: {
		getRoleBadgeProps(member) {
			let role = 'Member';
			if (this.$account.team.name == member.name) {
				role = 'Owner';
			}

			return {
				status: role,
				color: {
					Owner: 'blue',
					Member: 'gray'
				}[role]
			};
		},
		removeMember(member) {
			this.$confirm({
				title: 'Xóa thành viên',
				message: `Bạn có chắc chắn muốn loại bỏ ${member.first_name} ?`,
				actionLabel: 'Xóa',
				actionColor: 'red',
				action: closeDialog => {
					this.$resources.removeMember.submit({ user_email: member.name });
					closeDialog();
				}
			});
		},
		dropdownItems(member) {
			return [
				{
					label: 'Chỉnh sửa quyền',
					icon: 'edit',
					onClick: () => {
						this.memberName = member.name;
						this.showEditMemberDialog = true;
					}
				},
				{
					label: 'Xóa',
					icon: 'trash-2',
					onClick: () => this.removeMember(member)
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
		}
	}
};
</script>
