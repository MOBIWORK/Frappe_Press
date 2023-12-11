<template>
	<Card
		title="Đối tác MBW"
		subtitle="Đối tác MBW được liên kết với tài khoản của bạn"
		v-if="!$account.team.erpnext_partner"
	>
		<div>
			<ListItem
				:title="$account.partner_billing_name"
				:subtitle="$account.partner_email"
				v-if="$account.partner_email"
			>
			</ListItem>

			<div class="py-4">
				<h3 class="text-base text-gray-700" v-if="$account.parent_team">
					Chỉ nhóm cha mới có thể kết nối với đối tác MBW.
				</h3>
				<h3
					class="text-base text-gray-700"
					v-if="!$account.partner_email && !$account.parent_team"
				>
					Có mã giới thiệu đối tác MBW không? Nhấp vào
					<strong>Thêm mã đối tác</strong> để liên kết với nhóm đối tác của bạn.
				</h3>
			</div>
		</div>
		<template #actions>
			<Button
				@click="showPartnerReferralDialog = true"
				v-if="!$account.partner_email"
			>
				Thêm mã đối tác
			</Button>
		</template>
		<Dialog
			:options="{ title: 'Mã giới thiệu đối tác' }"
			v-model="showPartnerReferralDialog"
		>
			<template v-slot:body-content>
				<FormControl
					label="Nhập mã giới thiệu đối tác"
					type="input"
					v-model="referralCode"
					placeholder="e.g. rGjw3hJ81b"
					@input="referralCodeChange"
				/>
				<ErrorMessage class="mt-2" :message="$resources.addPartner.error" />
				<div class="mt-1">
					<div v-if="partnerExists" class="text-sm text-green-600" role="alert">
						Mã giới thiệu {{ referralCode }} thuộc về {{ partner }}
					</div>
					<ErrorMessage :message="errorMessage" />
				</div>
			</template>
			<template #actions>
				<Button
					variant="solid"
					:loading="$resources.addPartner.loading"
					loadingText="Đang lưu..."
					@click="$resources.addPartner.submit()"
				>
					Thêm đối tác
				</Button>
			</template>
		</Dialog>
	</Card>
</template>
<script>
import { notify } from '@/utils/toast';

export default {
	name: 'AccountPartner',
	data() {
		return {
			showPartnerReferralDialog: false,
			referralCode: null,
			partnerExists: false,
			errorMessage: null,
			partner: null
		};
	},
	resources: {
		addPartner() {
			return {
				url: 'press.api.account.add_partner',
				params: {
					referral_code: this.referralCode
				},
				onSuccess(res) {
					this.showPartnerReferralDialog = false;
					notify({
						title: 'Email đã được gửi đến đối tác',
						icon: 'check',
						color: 'green'
					});
				}
			};
		}
	},
	methods: {
		async referralCodeChange(e) {
			let code = e.target.value;
			this.partnerExists = false;

			let result = await this.$call('press.api.account.validate_partner_code', {
				code: code
			});

			let [isValidCode, partnerName] = result;

			if (isValidCode) {
				this.partnerExists = true;
				this.referralCode = code;
				this.partner = partnerName;
				this.partnerExists = true;
			} else {
				this.errorMessage = `${code} là mã giới thiệu không hợp lệ`;
			}
		}
	}
};
</script>
