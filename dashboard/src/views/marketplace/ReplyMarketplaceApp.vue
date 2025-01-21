<script setup>
import { reactive } from 'vue';
import { createResource } from 'frappe-ui';
import { translate } from '@/utils/index';

const props = defineProps({
	marketplaceApp: String,
	reviewId: String
});

const params = new Proxy(new URLSearchParams(window.location.search), {
	get: (searchParams, prop) => searchParams.get(prop)
});
let appTitle = params.title;

const reply = reactive({
	review: props.reviewId,
	reply: ''
});

const submitReply = createResource({
	url: 'press.api.marketplace.submit_developer_reply',
	validate() {
		if (!reply.reply) {
			return translate('ReplyMarketplaceApp_content_1');
		}
		if (!$account.team.is_developer) {
			return translate('ReplyMarketplaceApp_content_2');
		}
	},
	onSuccess() {
		window.location.href = `/marketplace/apps/${props.marketplaceApp}`;
	}
});
</script>

<template>
	<div class="px-4 py-4 text-base sm:px-8">
		<div>
			<h1 class="mb-4 text-xl font-semibold">
				{{ $t('ReplyMarketplaceApp_content_3') }}: {{ appTitle }}
			</h1>
		</div>

		<div class="mt-2 sm:grid sm:grid-cols-2">
			<div>
				<FormControl
					v-model="reply.reply"
					type="textarea"
					:label="$t('Write_Reply')"
				/>

				<ErrorMessage class="mt-2" :message="submitReply.error" />
				<Button
					class="mt-4 w-full"
					:loading="submitReply.loading"
					variant="solid"
					@click="submitReply.submit({ ...reply })"
					>{{ $t('Submit') }}</Button
				>
			</div>
		</div>
	</div>
</template>
