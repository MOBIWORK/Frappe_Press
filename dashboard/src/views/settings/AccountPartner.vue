<template>
	<Card
		:title="$t('AccountPartner_content_1')"
		:subtitle="$t('AccountPartner_content_2')"
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
					{{ $t('AccountPartner_content_3') }}
				</h3>
				<h3
					class="text-base text-gray-700"
					v-if="!$account.partner_email && !$account.parent_team"
				>
					{{ $t('AccountPartner_content_4') }}
					<strong>{{ $t('AccountPartner_content_5') }}</strong>
					{{ $t('AccountPartner_content_6') }}
				</h3>
			</div>
		</div>
		<template #actions>
			<Button
				@click="showPartnerReferralDialog = true"
				v-if="!$account.partner_email"
			>
				{{ $t('AccountPartner_content_5') }}
			</Button>
		</template>
		<Dialog
			:options="{ title: $t('AccountPartner_content_7') }"
			v-model="showPartnerReferralDialog"
		>
			<template v-slot:body-content>
				<FormControl
					:label="$t('AccountPartner_content_8')"
					type="input"
					v-model="referralCode"
					placeholder="e.g. rGjw3hJ81b"
					@input="referralCodeChange"
				/>
				<ErrorMessage class="mt-2" :message="$resources.addPartner.error" />
				<div class="mt-1">
					<div v-if="partnerExists" class="text-sm text-green-600" role="alert">
						{{ $t('AccountPartner_content_9') }} {{ referralCode }}
						{{ $t('AccountPartner_content_10') }} {{ partner }}
					</div>
					<ErrorMessage :message="errorMessage" />
				</div>
			</template>
			<template #actions>
				<Button
					variant="solid"
					:loading="$resources.addPartner.loading"
					:loadingText="`${$t('Saving')}...`"
					@click="$resources.addPartner.submit()"
				>
					{{ $t('Add_partner') }}
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
						title: this.$t('AccountPartner_content_11'),
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
				this.errorMessage = `${code} ${this.$t('AccountPartner_content_12')}`;
			}
		}
	}
};
</script>
