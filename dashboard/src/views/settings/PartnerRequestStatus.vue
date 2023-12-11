<template>
	<Card
		title="Trạng thái yêu cầu của đối tác"
		v-if="!$account.team.erpnext_partner"
	>
		<template #actions>
			<Badge
				:variant="'subtle'"
				:theme="this.partnerRequestStatus === 'Pending' ? 'orange' : 'green'"
				size="lg"
				:label="this.partnerRequestStatus"
				v-if="this.partnerRequestStatus"
			/>
		</template>
		<div class="flex items-center">
			<div v-if="$account.team.partnership_date">
				<span class="text-base">
					Ngày bắt đầu hợp tác với khách hàng:
					<span class="font-semibold">{{
						$date($account.team.partnership_date).toFormat('dd-MM-yyyy')
					}}</span>
				</span>
			</div>
			<div v-else>
				<span class="text-base">
					Để đặt ngày bắt đầu hợp tác với khách hàng, nhấp vào nút `Chỉnh
					sửa`</span
				>
			</div>
			<div class="ml-auto">
				<Button icon-left="edit" @click="showDateEditDialog = true">
					Chỉnh sửa
				</Button>
			</div>
		</div>

		<Dialog
			:options="{
				title: 'Cập nhật ngày bắt đầu hợp tác với khách hàng',
				actions: [
					{
						variant: 'solid',
						label: 'Lưu thay đổi',
						onClick: () => $resources.updatePartnershipDate.submit()
					}
				]
			}"
			v-model="showDateEditDialog"
		>
			<template v-slot:body-content>
				<FormControl
					label="Nhập ngày bắt đầu hợp tác"
					type="date"
					v-model="partnerDate"
					description="Ngày này sẽ được sử dụng để tính toán việc đạt được mục tiêu của đối tác của bạn."
				/>
				<ErrorMessage
					class="mt-2"
					:message="$resources.updatePartnershipDate.error"
				/>
			</template>
		</Dialog>
	</Card>
</template>
<script>
import { DateTime } from 'luxon';

export default {
	name: 'PartnerRequestStatus',
	data() {
		return {
			partnerRequestStatus: null,
			partnershipDate: null,
			showDateEditDialog: false,
			partnerDate: null
		};
	},
	resources: {
		getStatus: {
			url: 'press.api.account.get_partner_request_status',
			params: {
				team: $account.team.name
			},
			onSuccess(data) {
				this.partnerRequestStatus = data;
			},
			auto: true
		},
		updatePartnershipDate() {
			return {
				url: 'press.api.account.update_partnership_date',
				params: {
					team: $account.team.name,
					partnership_date: this.partnerDate || this.today
				},
				onSuccess() {
					this.showDateEditDialog = false;
				}
			};
		}
	},
	computed: {
		today() {
			return DateTime.local().toISODate();
		}
	}
};
</script>
