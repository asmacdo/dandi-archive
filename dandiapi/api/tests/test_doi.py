from __future__ import annotations

import pytest
from django.conf import settings

from dandiapi.api import datacite, doi


@pytest.mark.django_db
def test_generate_doi_data_version_doi_draft_event(published_version):
    """Test generating a Version DOI with draft event."""
    doi_string, datacite_payload = doi.generate_doi_data(
        version=published_version, version_doi=True, event=None
    )

    # Verify DOI string format for Version DOI
    dandiset_id = published_version.dandiset.identifier
    version_id = published_version.version
    prefix = settings.DANDI_DOI_API_PREFIX or '10.80507'
    expected_doi = f'{prefix}/dandi.{dandiset_id}/{version_id}'
    assert doi_string == expected_doi

    # Verify payload properties
    assert datacite_payload['data']['attributes']['doi'] == expected_doi
    assert datacite_payload['data']['attributes']['url'] == published_version.metadata['url']
    # For draft event, the 'event' field should be None or not present
    assert datacite_payload['data']['attributes'].get('event') is None


@pytest.mark.django_db
def test_generate_doi_data_version_doi_publish_event(published_version):
    """Test generating a Version DOI with publish event."""
    doi_string, datacite_payload = doi.generate_doi_data(
        version=published_version, version_doi=True, event='publish'
    )

    # Verify DOI string format for Version DOI
    dandiset_id = published_version.dandiset.identifier
    version_id = published_version.version
    prefix = settings.DANDI_DOI_API_PREFIX or '10.80507'
    expected_doi = f'{prefix}/dandi.{dandiset_id}/{version_id}'
    assert doi_string == expected_doi

    # Verify payload properties
    assert datacite_payload['data']['attributes']['doi'] == expected_doi
    assert datacite_payload['data']['attributes']['url'] == published_version.metadata['url']
    assert datacite_payload['data']['attributes']['event'] == 'publish'


@pytest.mark.django_db
def test_generate_doi_data_version_doi_hide_event(published_version):
    """Test generating a Version DOI with hide event."""
    doi_string, datacite_payload = doi.generate_doi_data(
        version=published_version, version_doi=True, event='hide'
    )

    # Verify DOI string format for Version DOI
    dandiset_id = published_version.dandiset.identifier
    version_id = published_version.version
    prefix = settings.DANDI_DOI_API_PREFIX or '10.80507'
    expected_doi = f'{prefix}/dandi.{dandiset_id}/{version_id}'
    assert doi_string == expected_doi

    # Verify payload properties
    assert datacite_payload['data']['attributes']['doi'] == expected_doi
    assert datacite_payload['data']['attributes']['url'] == published_version.metadata['url']
    assert datacite_payload['data']['attributes']['event'] == 'hide'


@pytest.mark.django_db
def test_generate_doi_data_dandiset_doi_draft_event(published_version):
    """Test generating a Dandiset DOI with draft event."""
    doi_string, datacite_payload = doi.generate_doi_data(
        version=published_version, version_doi=False, event=None
    )

    # Verify DOI string format for Dandiset DOI
    dandiset_id = published_version.dandiset.identifier
    prefix = settings.DANDI_DOI_API_PREFIX or '10.80507'
    expected_doi = f'{prefix}/dandi.{dandiset_id}'
    assert doi_string == expected_doi

    # Verify payload properties
    assert datacite_payload['data']['attributes']['doi'] == expected_doi
    # URL should be the Dandiset URL (without version)
    expected_url = published_version.metadata['url'].rsplit('/', 1)[0]
    assert datacite_payload['data']['attributes']['url'] == expected_url
    # For draft event, the 'event' field should be None or not present
    assert datacite_payload['data']['attributes'].get('event') is None


@pytest.mark.django_db
def test_generate_doi_data_dandiset_doi_publish_event(published_version):
    """Test generating a Dandiset DOI with publish event."""
    doi_string, datacite_payload = doi.generate_doi_data(
        version=published_version, version_doi=False, event='publish'
    )

    # Verify DOI string format for Dandiset DOI
    dandiset_id = published_version.dandiset.identifier
    prefix = settings.DANDI_DOI_API_PREFIX or '10.80507'
    expected_doi = f'{prefix}/dandi.{dandiset_id}'
    assert doi_string == expected_doi

    # Verify payload properties
    assert datacite_payload['data']['attributes']['doi'] == expected_doi
    # URL should be the Dandiset URL (without version)
    expected_url = published_version.metadata['url'].rsplit('/', 1)[0]
    assert datacite_payload['data']['attributes']['url'] == expected_url
    assert datacite_payload['data']['attributes']['event'] == 'publish'


@pytest.mark.django_db
def test_generate_doi_data_dandiset_doi_hide_event(published_version):
    """Test generating a Dandiset DOI with hide event."""
    doi_string, datacite_payload = doi.generate_doi_data(
        version=published_version, version_doi=False, event='hide'
    )

    # Verify DOI string format for Dandiset DOI
    dandiset_id = published_version.dandiset.identifier
    prefix = settings.DANDI_DOI_API_PREFIX or '10.80507'
    expected_doi = f'{prefix}/dandi.{dandiset_id}'
    assert doi_string == expected_doi

    # Verify payload properties
    assert datacite_payload['data']['attributes']['doi'] == expected_doi
    # URL should be the Dandiset URL (without version)
    expected_url = published_version.metadata['url'].rsplit('/', 1)[0]
    assert datacite_payload['data']['attributes']['url'] == expected_url
    assert datacite_payload['data']['attributes']['event'] == 'hide'


@pytest.mark.django_db
def test_generate_doi_data_url_handling_version_doi(published_version):
    """Test URL handling for Version DOIs."""
    _, datacite_payload = doi.generate_doi_data(version=published_version, version_doi=True)

    # URL should be the complete Version URL (with version)
    expected_url = published_version.metadata['url']
    assert datacite_payload['data']['attributes']['url'] == expected_url


@pytest.mark.django_db
def test_generate_doi_data_url_handling_dandiset_doi(published_version):
    """Test URL handling for Dandiset DOIs."""
    _, datacite_payload = doi.generate_doi_data(version=published_version, version_doi=False)

    # URL should be the Dandiset URL (without version)
    expected_url = published_version.metadata['url'].rsplit('/', 1)[0]
    assert datacite_payload['data']['attributes']['url'] == expected_url


@pytest.mark.django_db
def test_datacite_payload_structure(published_version):
    """Test the structure of the datacite payload."""
    _, datacite_payload = doi.generate_doi_data(version=published_version, version_doi=True)

    # Test the basic structure of the payload
    assert 'data' in datacite_payload
    assert 'attributes' in datacite_payload['data']
    assert 'type' in datacite_payload['data']
    assert datacite_payload['data']['type'] == 'dois'

    # Test that to_datacite was called correctly by checking required fields
    attributes = datacite_payload['data']['attributes']
    assert 'titles' in attributes
    assert 'creators' in attributes
    assert 'publisher' in attributes
    assert 'publicationYear' in attributes
    assert 'types' in attributes
    assert 'url' in attributes


@pytest.mark.django_db
def test_delete_or_hide_doi_draft(mocker, published_version):
    """Test deleting a draft DOI."""
    # Mock the is_configured method to return True
    mocker.patch.object(doi.datacite_client, 'is_configured', return_value=True)
    
    # Mock requests.get to simulate a draft DOI response
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        'data': {'attributes': {'state': 'draft'}}
    }
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch('requests.get', return_value=mock_response)
    
    # Mock requests.delete for the API call
    mock_delete = mocker.patch('requests.delete')
    mock_delete_response = mocker.Mock()
    mock_delete_response.raise_for_status = mocker.Mock()
    mock_delete.return_value = mock_delete_response
    
    # Call the function
    doi = '10.80507/dandi.test'
    doi.delete_or_hide_doi(doi)
    
    # Verify delete was called with the correct parameters
    mock_delete.assert_called_once()
    assert doi in mock_delete.call_args[0][0]


@pytest.mark.django_db
def test_delete_or_hide_doi_findable(mocker, published_version):
    """Test hiding a findable DOI."""
    # Mock the is_configured method to return True
    mocker.patch.object(doi.datacite_client, 'is_configured', return_value=True)
    mocker.patch('django.conf.settings.DANDI_DOI_PUBLISH', True)
    
    # Mock requests.get to simulate a findable DOI response
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        'data': {'attributes': {'state': 'findable'}}
    }
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch('requests.get', return_value=mock_response)
    
    # Mock requests.put for the API call
    mock_put = mocker.patch('requests.put')
    mock_put_response = mocker.Mock()
    mock_put_response.raise_for_status = mocker.Mock()
    mock_put.return_value = mock_put_response
    
    # Call the function
    doi = '10.80507/dandi.test'
    doi.delete_or_hide_doi(doi)
    
    # Verify put was called with the correct parameters (hide event)
    mock_put.assert_called_once()
    assert doi in mock_put.call_args[0][0]
    assert 'event' in mock_put.call_args[1]['json']['data']['attributes']
    assert mock_put.call_args[1]['json']['data']['attributes']['event'] == 'hide'


@pytest.mark.django_db
def test_delete_or_hide_doi_findable_publish_disabled(mocker, published_version):
    """Test that a findable DOI is not hidden when DANDI_DOI_PUBLISH is False."""
    # Mock the is_configured method to return True
    mocker.patch.object(doi.datacite_client, 'is_configured', return_value=True)
    mocker.patch('django.conf.settings.DANDI_DOI_PUBLISH', False)
    
    # Mock requests.get to simulate a findable DOI response
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        'data': {'attributes': {'state': 'findable'}}
    }
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch('requests.get', return_value=mock_response)
    
    # Mock requests.put for the API call
    mock_put = mocker.patch('requests.put')
    
    # Call the function
    doi = '10.80507/dandi.test'
    doi.delete_or_hide_doi(doi)
    
    # Verify put was not called since DANDI_DOI_PUBLISH is False
    mock_put.assert_not_called()